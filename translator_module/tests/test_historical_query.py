"""Unit tests for the historical-query foundation."""

import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from translator_module.revision import (
    GitRevisionSource,
    GitSourceError,
    OksSnapshot,
    ResolvedRevision,
    RevisionRequest,
    WorkingTreeSource,
)


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

    def test_missing_historical_file_has_a_clear_error(self):
        source = GitRevisionSource(self.root, self.old_commit)

        with self.assertRaisesRegex(GitSourceError, "missing.xml"):
            source.read_bytes("missing.xml")

    def test_invalid_repository_or_revision_fails_early(self):
        with self.assertRaises(GitSourceError):
            GitRevisionSource(self.root / "missing", self.old_commit)
        with self.assertRaises(GitSourceError):
            GitRevisionSource(self.root, "not-a-real-revision")


if __name__ == "__main__":
    unittest.main()
