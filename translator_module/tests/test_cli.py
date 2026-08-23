"""Tests for CLI argument parsing without starting the LLM."""

import unittest
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from translator_module import cli
from translator_module.revision import OksSnapshot, ResolvedRevision, WorkingTreeSource


class CliArgumentTests(unittest.TestCase):
    def test_commit_hash_builds_revision_request(self):
        args = cli.build_argument_parser().parse_args(
            ["--commit-hash", "abc123", "--repo", "G:/repo"]
        )
        request = cli.build_revision_request(args)

        self.assertEqual(request.commit_hash, "abc123")
        self.assertEqual(request.ref, "main")

    def test_date_requires_and_preserves_timezone(self):
        args = cli.build_argument_parser().parse_args(
            ["--date", "2026-08-01T12:00:00+05:45"]
        )
        request = cli.build_revision_request(args)

        self.assertEqual(
            request.date,
            datetime.fromisoformat("2026-08-01T12:00:00+05:45"),
        )

    def test_zulu_date_is_parsed_as_utc(self):
        args = cli.build_argument_parser().parse_args(
            ["--date", "2026-08-01T06:15:00Z"]
        )

        self.assertEqual(args.date.tzinfo, timezone.utc)

    def test_revision_selectors_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit):
            cli.build_argument_parser().parse_args(
                ["--commit-hash", "abc123", "--tag", "v1"]
            )

    def test_run_id_preserves_run_map_and_ref(self):
        args = cli.build_argument_parser().parse_args(
            ["--run-id", "48192", "--run-map", "runs.json", "--ref", "release"]
        )
        request = cli.build_revision_request(args)

        self.assertEqual(request.run_id, "48192")
        self.assertEqual(args.run_map, "runs.json")
        self.assertEqual(request.ref, "release")

    def test_naive_date_is_rejected(self):
        with self.assertRaises(SystemExit):
            cli.build_argument_parser().parse_args(
                ["--date", "2026-08-01T12:00:00"]
            )

    def test_execution_options_accept_repeatable_data_paths(self):
        args = cli.build_argument_parser().parse_args(
            [
                "--commit-hash",
                "abc123",
                "--execute",
                "--data-path",
                "test_data/one.data.xml",
                "--data-path",
                "test_data/two.data.xml",
                "--target-class",
                "Application",
                "--oks-dump-executable",
                "C:/oks/bin/oks_dump",
                "--execution-timeout",
                "12.5",
            ]
        )

        self.assertTrue(args.execute)
        self.assertEqual(
            args.data_path,
            ["test_data/one.data.xml", "test_data/two.data.xml"],
        )
        self.assertEqual(args.target_class, "Application")
        self.assertEqual(args.oks_dump_executable, "C:/oks/bin/oks_dump")
        self.assertEqual(args.execution_timeout, 12.5)

    def test_execution_requires_historical_selector(self):
        self.assertEqual(cli.main(["--execute"]), 2)

    def test_execution_timeout_must_be_positive_and_finite(self):
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(value=value):
                with self.assertRaises(SystemExit):
                    cli.build_argument_parser().parse_args(
                        ["--execution-timeout", value]
                    )

    def test_execution_helper_passes_historical_context_to_oks_dump(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "schema.xml").write_text(
                "<oks-schema><class name='Application' /></oks-schema>",
                encoding="utf-8",
            )
            source = WorkingTreeSource(root)
            revision = ResolvedRevision(
                repository=root.resolve(),
                commit="a" * 40,
                requested_as="commit",
            )
            snapshot = OksSnapshot(
                revision=revision,
                schema_paths=("schema.xml",),
                data_paths=(),
                source=source,
            )
            args = cli.build_argument_parser().parse_args(
                ["--commit-hash", "abc123", "--execute"]
            )
            result = {
                "oks_query": '(all (object-id "app-1" =))',
                "ir": {"target_class": "Application"},
            }
            expected = SimpleNamespace(
                revision="a" * 40,
                stdout="app-1\n",
                stderr="",
            )

            with patch(
                "translator_module.execution.OksDumpExecutor.execute",
                return_value=expected,
            ) as execute:
                actual = cli._execute_historical_result(args, result, snapshot)

        self.assertIs(actual, expected)
        context = execute.call_args.args[0]
        self.assertEqual(context.target_class, "Application")
        self.assertEqual(context.snapshot, snapshot)
        self.assertEqual(context.oks_query, result["oks_query"])

    def test_execution_helper_rejects_target_absent_from_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "schema.xml").write_text(
                "<oks-schema><class name='Application' /></oks-schema>",
                encoding="utf-8",
            )
            source = WorkingTreeSource(root)
            revision = ResolvedRevision(root.resolve(), "a" * 40, "commit")
            snapshot = OksSnapshot(
                revision=revision,
                schema_paths=("schema.xml",),
                source=source,
            )
            args = cli.build_argument_parser().parse_args(
                ["--commit-hash", "abc123", "--execute"]
            )

            with self.assertRaisesRegex(ValueError, "Missing"):
                cli._execute_historical_result(
                    args,
                    {
                        "oks_query": "(all (object-id \"x\" =))",
                        "ir": {"target_class": "Missing"},
                    },
                    snapshot,
                )
