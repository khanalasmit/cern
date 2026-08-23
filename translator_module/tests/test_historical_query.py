"""Unit tests for the historical-query foundation."""

import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

from translator_module.revision import (
    GitRevisionSource,
    GitSourceError,
    GitRevisionResolver,
    OksSnapshot,
    ResolvedRevision,
    RevisionResolutionError,
    RunRegistryError,
    RunRevisionRegistry,
    RevisionRequest,
    WorkingTreeSource,
)
from translator_module.revision import SnapshotBuilder, SnapshotError
from translator_module.execution import (
    HistoricalOksExecutor,
    HistoricalDataLoader,
    HistoricalExecutionContext,
    OksExecutionError,
    OksDumpError,
    OksDumpExecutor,
)
from translator_module.execution.context import ExecutionContextError
from translator_module.rag.schema_loader import SchemaLoadError, SchemaLoader
from translator_module.agent.few_shot import FewShotManager
from unittest.mock import patch
import numpy as np

try:
    from translator_module.rag.ingest import HybridIndexer
    RAG_IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    HybridIndexer = None
    RAG_IMPORT_ERROR = str(exc)


REPO_ROOT = Path(__file__).resolve().parents[2]


class RevisionModelTests(unittest.TestCase):
    def test_revision_request_has_safe_defaults(self):
        request = RevisionRequest()

        self.assertIsNone(request.commit_hash)
        self.assertIsNone(request.tag)
        self.assertIsNone(request.date)
        self.assertIsNone(request.run_id)
        self.assertEqual(request.ref, "main")

    def test_resolved_revision_is_immutable(self):
        revision = ResolvedRevision(
            repository=Path("/repo"),
            commit="a" * 40,
            requested_as="commit",
            commit_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        with self.assertRaises(FrozenInstanceError):
            revision.commit = "b" * 40

    def test_snapshot_defaults_to_empty_file_lists(self):
        revision = ResolvedRevision(Path("/repo"), "a" * 40, "current")
        snapshot = OksSnapshot(revision)

        self.assertEqual(snapshot.schema_paths, ())
        self.assertEqual(snapshot.data_paths, ())


class WorkingTreeSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "schemas").mkdir()
        (self.root / "schemas" / "application.schema.xml").write_text(
            "<schema />", encoding="utf-8"
        )
        (self.root / "config.data.xml").write_text(
            "<data />", encoding="utf-8"
        )
        self.source = WorkingTreeSource(self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_reads_bytes_and_opens_binary_stream(self):
        self.assertEqual(
            self.source.read_bytes("schemas/application.schema.xml"),
            b"<schema />",
        )
        with self.source.open_binary("config.data.xml") as stream:
            self.assertEqual(stream.read(), b"<data />")

    def test_checks_existence_and_lists_files(self):
        self.assertTrue(self.source.exists("config.data.xml"))
        self.assertFalse(self.source.exists("missing.xml"))
        self.assertEqual(
            self.source.list_files("**/*.schema.xml"),
            ["schemas/application.schema.xml"],
        )

    def test_rejects_unsafe_paths(self):
        with self.assertRaises(ValueError):
            self.source.read_bytes("../outside.xml")
        with self.assertRaises(ValueError):
            self.source.read_bytes(str(self.root / "config.data.xml"))
        with self.assertRaises(ValueError):
            self.source.list_files("../**/*.xml")


class SchemaLoaderTests(unittest.TestCase):
    def test_loads_existing_scraped_wrapper(self):
        documents = SchemaLoader.load_file(
            REPO_ROOT / "oks_scraped" / "oks_schema_examples.xml"
        )

        self.assertGreater(len(documents), 0)
        self.assertTrue(any(document.root.findall(".//class") for document in documents))
        self.assertTrue(all("::" in document.source_path for document in documents))

    def test_loads_standalone_schema_through_working_tree_source(self):
        source = WorkingTreeSource(REPO_ROOT)
        documents = SchemaLoader.load_source(
            source,
            ["test_schema/xml/aal.schema.xml"],
        )

        self.assertEqual(len(documents), 1)
        self.assertGreater(len(documents[0].root.findall(".//class")), 0)
        self.assertEqual(documents[0].source_path, "test_schema/xml/aal.schema.xml")

    def test_reports_malformed_xml_with_source_and_location(self):
        with self.assertRaisesRegex(SchemaLoadError, "broken.xml.*line"):
            SchemaLoader.load_bytes(b"<broken>", "broken.xml")


class HistoricalFewShotTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = WorkingTreeSource(self.root)
        (self.root / "gold_pairs.jsonl").write_text(
            '{"question":"old question","query_oks":"(all (object-id \\\"old-1\\\" =))"}\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_loads_examples_from_revision_source(self):
        manager = FewShotManager.from_source(
            self.source,
            "gold_pairs.jsonl",
        )

        self.assertEqual(len(manager.examples), 1)
        self.assertIn("old question", manager.get_examples("old question"))

    def test_missing_revision_examples_are_empty_without_working_tree_fallback(self):
        manager = FewShotManager.from_source(
            self.source,
            "missing-gold-pairs.jsonl",
        )

        self.assertEqual(manager.get_examples("anything"), "No examples available.")


class HistoricalSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "test_schema").mkdir()
        (self.root / "test_data").mkdir()
        (self.root / "test_schema" / "application.schema.xml").write_text(
            "<oks-schema><class name='Application' /></oks-schema>",
            encoding="utf-8",
        )
        (self.root / "test_data" / "application.data.xml").write_text(
            "<oks-data><obj class='Application' id='app-1' /></oks-data>",
            encoding="utf-8",
        )
        self.source = WorkingTreeSource(self.root)
        self.revision = ResolvedRevision(
            repository=self.root.resolve(),
            commit="a" * 40,
            requested_as="current",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_builder_discovers_schema_and_data_from_one_source(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)

        self.assertEqual(snapshot.schema_paths, ("test_schema/application.schema.xml",))
        self.assertEqual(snapshot.data_paths, ("test_data/application.data.xml",))
        self.assertIs(snapshot.source, self.source)

    def test_builder_rejects_missing_required_files(self):
        with self.assertRaisesRegex(SnapshotError, "missing data"):
            SnapshotBuilder().build(
                self.source,
                self.revision,
                data_paths=["test_data/missing.data.xml"],
            )

    def test_data_loader_reads_historical_data_documents(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        documents = HistoricalDataLoader.load_source(
            self.source,
            snapshot.data_paths,
        )

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].source_path, "test_data/application.data.xml")
        self.assertEqual(documents[0].root.find(".//obj").get("id"), "app-1")

    def test_execution_context_loads_only_snapshot_data(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        context = HistoricalExecutionContext(
            snapshot=snapshot,
            oks_query="(all (object-id \"app-1\" =))",
            target_class="Application",
        )

        documents = context.load_data()

        self.assertEqual(len(documents), 1)
        self.assertEqual(context.target_class, "Application")

    def test_execution_context_requires_a_source(self):
        snapshot = OksSnapshot(
            revision=self.revision,
            schema_paths=("test_schema/application.schema.xml",),
            data_paths=("test_data/application.data.xml",),
        )
        context = HistoricalExecutionContext(snapshot, "(all (object-id \"app-1\" =))")

        with self.assertRaises(ExecutionContextError):
            context.load_data()

    def test_execution_context_requires_target_class(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        context = HistoricalExecutionContext(
            snapshot=snapshot,
            oks_query="(all (object-id \"app-1\" =))",
        )

        with self.assertRaises(ExecutionContextError):
            context.require_target_class()

    def test_executor_requires_a_native_backend(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        context = HistoricalExecutionContext(
            snapshot=snapshot,
            oks_query="(all (object-id \"app-1\" =))",
            target_class="Application",
        )

        with self.assertRaises(OksExecutionError):
            HistoricalOksExecutor().execute(context)

    def test_executor_passes_historical_context_to_backend(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        context = HistoricalExecutionContext(
            snapshot=snapshot,
            oks_query="(all (object-id \"app-1\" =))",
            target_class="Application",
        )

        class RecordingBackend:
            def __init__(self):
                self.received = None

            def execute(self, **kwargs):
                self.received = kwargs
                return [{"id": "app-1"}]

        backend = RecordingBackend()
        result = HistoricalOksExecutor(backend).execute(context)

        self.assertEqual(result.revision, "a" * 40)
        self.assertEqual(result.target_class, "Application")
        self.assertEqual(result.rows, ({"id": "app-1"},))
        self.assertIs(backend.received["snapshot"], snapshot)
        self.assertEqual(backend.received["oks_query"], context.oks_query)

    def test_oks_dump_executor_builds_safe_command_and_returns_raw_output(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        context = HistoricalExecutionContext(
            snapshot=snapshot,
            oks_query="(all (object-id \"app-1\" =))",
            target_class="Application",
        )

        completed = subprocess.CompletedProcess(
            args=["oks_dump"],
            returncode=0,
            stdout="app-1\n",
            stderr="",
        )
        with patch(
            "translator_module.execution.oks_dump.subprocess.run",
            return_value=completed,
        ) as run:
            result = OksDumpExecutor().execute(context)

        self.assertEqual(result.stdout, "app-1\n")
        self.assertEqual(result.revision, "a" * 40)
        command = run.call_args.args[0]
        self.assertEqual(
            command[:5],
            ["oks_dump", "--class", "Application", "--query", context.oks_query],
        )
        self.assertEqual(
            command[-1],
            str((self.root / "test_data" / "application.data.xml").resolve()),
        )
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_oks_dump_executor_reports_missing_runtime(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        context = HistoricalExecutionContext(
            snapshot=snapshot,
            oks_query="(all (object-id \"app-1\" =))",
            target_class="Application",
        )

        with patch(
            "translator_module.execution.oks_dump.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            with self.assertRaisesRegex(OksDumpError, "not found"):
                OksDumpExecutor().execute(context)

    def test_oks_dump_executor_reports_native_failure_code(self):
        snapshot = SnapshotBuilder().build(self.source, self.revision)
        context = HistoricalExecutionContext(
            snapshot=snapshot,
            oks_query="(all (object-id \"app-1\" =))",
            target_class="Application",
        )
        completed = subprocess.CompletedProcess(
            args=["oks_dump"],
            returncode=3,
            stdout="",
            stderr="invalid query",
        )

        with patch(
            "translator_module.execution.oks_dump.subprocess.run",
            return_value=completed,
        ):
            with self.assertRaisesRegex(OksDumpError, "bad query"):
                OksDumpExecutor().execute(context)


@unittest.skipUnless(
    HybridIndexer is not None,
    f"RAG dependencies are not installed: {RAG_IMPORT_ERROR}",
)
class SourceAwareIndexerTests(unittest.TestCase):
    class FakeEncoder:
        def encode(self, values, **kwargs):
            return np.zeros((len(values), 4), dtype="float32")

    def test_ingest_source_builds_revision_metadata(self):
        source = WorkingTreeSource(REPO_ROOT)

        with patch(
            "translator_module.rag.ingest.SentenceTransformer",
            return_value=self.FakeEncoder(),
        ):
            indexer = HybridIndexer()
            indexer.ingest_source(
                source,
                ["test_schema/xml/aal.schema.xml"],
                revision="a" * 40,
            )

        self.assertGreater(len(indexer.chunks), 0)
        self.assertTrue(
            all(chunk.metadata["source_path"] == "test_schema/xml/aal.schema.xml"
                for chunk in indexer.chunks)
        )
        self.assertTrue(
            all(chunk.metadata["revision"] == "a" * 40 for chunk in indexer.chunks)
        )

    def test_ingest_xml_preserves_existing_wrapper_behavior(self):
        with patch(
            "translator_module.rag.ingest.SentenceTransformer",
            return_value=self.FakeEncoder(),
        ):
            indexer = HybridIndexer()
            indexer.ingest_xml(
                str(REPO_ROOT / "oks_scraped" / "oks_schema_examples.xml")
            )

        self.assertGreater(len(indexer.chunks), 0)


class GitRevisionSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self._run_git("init", "--quiet")
        self._run_git("config", "user.email", "historical-query@example.test")
        self._run_git("config", "user.name", "Historical Query Tests")

        (self.root / "schemas").mkdir()
        (self.root / "schemas" / "application.schema.xml").write_text(
            "<schema version='old' />", encoding="utf-8"
        )
        (self.root / "config.data.xml").write_text(
            "<data version='old' />", encoding="utf-8"
        )
        self._run_git("add", ".")
        self._run_git("commit", "--quiet", "-m", "old configuration")
        self.old_commit = self._git_output("rev-parse", "HEAD")

        (self.root / "schemas" / "application.schema.xml").write_text(
            "<schema version='new' />", encoding="utf-8"
        )
        (self.root / "config.data.xml").write_text(
            "<data version='new' />", encoding="utf-8"
        )
        self._run_git("add", ".")
        self._run_git("commit", "--quiet", "-m", "new configuration")
        self.new_commit = self._git_output("rev-parse", "HEAD")
        self.head_before_reads = self.new_commit

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_git(self, *arguments):
        return subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def _git_output(self, *arguments):
        return self._run_git(*arguments).stdout.decode("ascii").strip()

    def test_reads_exact_bytes_from_each_commit(self):
        old_source = GitRevisionSource(self.root, self.old_commit)
        new_source = GitRevisionSource(self.root, self.new_commit)

        self.assertEqual(old_source.commit, self.old_commit)
        self.assertEqual(
            old_source.read_bytes("schemas/application.schema.xml"),
            b"<schema version='old' />",
        )
        self.assertEqual(
            new_source.read_bytes("schemas/application.schema.xml"),
            b"<schema version='new' />",
        )
        with old_source.open_binary("config.data.xml") as stream:
            self.assertEqual(stream.read(), b"<data version='old' />")

    def test_exists_and_lists_historical_files(self):
        source = GitRevisionSource(self.root, self.old_commit)

        self.assertTrue(source.exists("config.data.xml"))
        self.assertFalse(source.exists("missing.xml"))
        self.assertEqual(
            source.list_files("schemas/*.schema.xml"),
            ["schemas/application.schema.xml"],
        )

    def test_reads_do_not_change_current_head_or_working_tree(self):
        source = GitRevisionSource(self.root, self.old_commit)

        source.read_bytes("config.data.xml")
        source.list_files("**/*.xml")

        self.assertEqual(self._git_output("rev-parse", "HEAD"), self.head_before_reads)
        self.assertEqual(
            (self.root / "config.data.xml").read_text(encoding="utf-8"),
            "<data version='new' />",
        )

    def test_git_source_materializes_historical_files_without_checkout(self):
        source = GitRevisionSource(self.root, self.old_commit)

        with source.materialize() as materialized:
            self.assertEqual(
                (materialized / "config.data.xml").read_text(encoding="utf-8"),
                "<data version='old' />",
            )

        self.assertEqual(self._git_output("rev-parse", "HEAD"), self.head_before_reads)

    def test_missing_historical_file_has_a_clear_error(self):
        source = GitRevisionSource(self.root, self.old_commit)

        with self.assertRaisesRegex(GitSourceError, "missing.xml"):
            source.read_bytes("missing.xml")

    def test_invalid_repository_or_revision_fails_early(self):
        with self.assertRaises(GitSourceError):
            GitRevisionSource(self.root / "missing", self.old_commit)
        with self.assertRaises(GitSourceError):
            GitRevisionSource(self.root, "not-a-real-revision")


class GitRevisionResolverTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self._run_git("init", "--quiet", "-b", "main")
        self._run_git("config", "user.email", "historical-query@example.test")
        self._run_git("config", "user.name", "Historical Query Tests")

        (self.root / "configuration.xml").write_text(
            "<configuration version='old' />", encoding="utf-8"
        )
        self._commit("old configuration", "2026-01-01T10:00:00+00:00")
        self.old_commit = self._git_output("rev-parse", "HEAD")
        self._run_git("tag", "v-old")

        (self.root / "configuration.xml").write_text(
            "<configuration version='new' />", encoding="utf-8"
        )
        self._commit("new configuration", "2026-02-01T10:00:00+00:00")
        self.new_commit = self._git_output("rev-parse", "HEAD")

        self.resolver = GitRevisionResolver(self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_git(self, *arguments, env=None):
        return subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    def _git_output(self, *arguments):
        return self._run_git(*arguments).stdout.decode("ascii").strip()

    def _commit(self, message, timestamp):
        self._run_git("add", ".")
        environment = os.environ.copy()
        environment["GIT_AUTHOR_DATE"] = timestamp
        environment["GIT_COMMITTER_DATE"] = timestamp
        self._run_git("commit", "--quiet", "-m", message, env=environment)

    def test_resolves_exact_commit_to_full_sha(self):
        resolved = self.resolver.resolve(
            RevisionRequest(commit_hash=self.old_commit[:10])
        )

        self.assertEqual(resolved.commit, self.old_commit)
        self.assertEqual(resolved.requested_as, "commit")
        self.assertEqual(resolved.repository, self.root.resolve())
        self.assertEqual(
            resolved.commit_date,
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        )

    def test_resolves_tag_to_tagged_commit(self):
        resolved = self.resolver.resolve(RevisionRequest(tag="v-old"))

        self.assertEqual(resolved.commit, self.old_commit)
        self.assertEqual(resolved.requested_as, "tag")

    def test_resolves_date_to_latest_commit_at_or_before_timestamp(self):
        before_new = self.resolver.resolve(
            RevisionRequest(
                date=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
                ref="main",
            )
        )
        after_new = self.resolver.resolve(
            RevisionRequest(
                date=datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc),
                ref="main",
            )
        )

        self.assertEqual(before_new.commit, self.old_commit)
        self.assertEqual(after_new.commit, self.new_commit)
        self.assertEqual(before_new.requested_as, "date")

    def test_no_selector_resolves_current_head(self):
        resolved = self.resolver.resolve()

        self.assertEqual(resolved.commit, self.new_commit)
        self.assertEqual(resolved.requested_as, "current")

    def test_rejects_ambiguous_or_unsupported_requests(self):
        with self.assertRaisesRegex(RevisionResolutionError, "mutually exclusive"):
            self.resolver.resolve(
                RevisionRequest(commit_hash=self.old_commit, tag="v-old")
            )
        with self.assertRaisesRegex(RevisionResolutionError, "run_id"):
            self.resolver.resolve(RevisionRequest(run_id="48192"))

    def test_resolves_run_id_from_explicit_registry(self):
        registry_path = self.root / "run_revisions.json"
        registry_path.write_text(
            json.dumps(
                {
                    "48192": {
                        "commit": self.old_commit,
                        "timestamp": "2026-01-01T10:00:00+00:00",
                    }
                }
            ),
            encoding="utf-8",
        )
        registry = RunRevisionRegistry.from_json(registry_path)
        resolved = GitRevisionResolver(self.root, run_registry=registry).resolve(
            RevisionRequest(run_id="48192")
        )

        self.assertEqual(resolved.commit, self.old_commit)
        self.assertEqual(resolved.requested_as, "run_id")
        self.assertEqual(resolved.run_id, "48192")

    def test_run_registry_rejects_missing_and_malformed_entries(self):
        with self.assertRaises(RunRegistryError):
            RunRevisionRegistry.from_mapping({"48192": {"timestamp": "missing commit"}})
        with self.assertRaises(RunRegistryError):
            RunRevisionRegistry.from_mapping({"48192": {"commit": "bad commit"}})
        with self.assertRaises(RunRegistryError):
            RunRevisionRegistry.from_mapping(["not an object"])

        registry = RunRevisionRegistry.from_mapping({"48192": self.old_commit})
        with self.assertRaisesRegex(RunRegistryError, "not present"):
            registry.resolve("99999")

    def test_run_id_with_invalid_registered_commit_fails_resolution(self):
        registry = RunRevisionRegistry.from_mapping({"48192": "not-a-real-commit"})

        with self.assertRaises(RevisionResolutionError):
            GitRevisionResolver(self.root, run_registry=registry).resolve(
                RevisionRequest(run_id="48192")
            )

    def test_rejects_invalid_date_or_missing_history(self):
        with self.assertRaisesRegex(RevisionResolutionError, "timezone-aware"):
            self.resolver.resolve(RevisionRequest(date=datetime(2026, 1, 15)))
        with self.assertRaises(RevisionResolutionError):
            self.resolver.resolve(
                RevisionRequest(
                    date=datetime(2025, 1, 1, tzinfo=timezone.utc),
                    ref="main",
                )
            )

    def test_invalid_repository_fails_before_resolution(self):
        with self.assertRaises(RevisionResolutionError):
            GitRevisionResolver(self.root / "missing")


if __name__ == "__main__":
    unittest.main()
