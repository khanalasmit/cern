"""Revision and source abstractions for historical OKS queries."""

from .models import OksSnapshot, ResolvedRevision, RevisionRequest
from .source import FileSource, WorkingTreeSource
from .git_source import GitRevisionSource, GitSourceError
from .resolver import GitRevisionResolver, RevisionResolutionError
from .run_registry import RunRevision, RunRevisionRegistry, RunRegistryError
from .snapshot import SnapshotBuilder, SnapshotError, SnapshotPatterns

__all__ = [
    "FileSource",
    "GitRevisionSource",
    "GitSourceError",
    "GitRevisionResolver",
    "RevisionResolutionError",
    "RunRevision",
    "RunRevisionRegistry",
    "RunRegistryError",
    "SnapshotBuilder",
    "SnapshotError",
    "SnapshotPatterns",
    "OksSnapshot",
    "ResolvedRevision",
    "RevisionRequest",
    "WorkingTreeSource",
]
