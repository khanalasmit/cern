"""Unit tests for the historical-query foundation."""

import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

from translator_module.revision import (
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


if __name__ == "__main__":
    unittest.main()
