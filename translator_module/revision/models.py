"""Data contracts used by the historical-query revision layer."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .source import FileSource


@dataclass(frozen=True)
class RevisionRequest:
    """A user request for a repository revision.

    The resolver will later enforce that at most one selector is supplied.
    Keeping this object as a data-only contract makes the resolver easy to
    test independently from the CLI.
    """

    commit_hash: Optional[str] = None
    tag: Optional[str] = None
    date: Optional[datetime] = None
    run_id: Optional[str] = None
    ref: str = "main"


@dataclass(frozen=True)
class ResolvedRevision:
    """An immutable, auditable result of resolving a revision request."""

    repository: Path
    commit: str
    requested_as: str
    ref: str = "main"
    commit_date: Optional[datetime] = None
    run_id: Optional[str] = None


@dataclass(frozen=True)
class OksSnapshot:
    """The schema and data paths belonging to one resolved revision."""

    revision: ResolvedRevision
    schema_paths: tuple[str, ...] = ()
    data_paths: tuple[str, ...] = ()
    source: Optional[FileSource] = None
