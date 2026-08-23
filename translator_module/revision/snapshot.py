"""Discover a consistent schema/data file set for one revision."""

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from .models import OksSnapshot, ResolvedRevision
from .source import FileSource


class SnapshotError(ValueError):
    """Raised when a revision does not contain a usable OKS snapshot."""


@dataclass(frozen=True)
class SnapshotPatterns:
    schema: tuple[str, ...] = ("test_schema/**/*.schema.xml",)
    data: tuple[str, ...] = ("test_data/**/*.data.xml",)


class SnapshotBuilder:
    """Build an immutable snapshot from one source and one revision."""

    def __init__(self, patterns: SnapshotPatterns | None = None):
        self.patterns = patterns or SnapshotPatterns()

    @staticmethod
    def _explicit_or_discovered(
        source: FileSource,
        explicit_paths: Optional[Sequence[str]],
        patterns: Iterable[str],
        kind: str,
    ) -> tuple[str, ...]:
        if explicit_paths is not None:
            paths = tuple(sorted(set(explicit_paths)))
            missing = [path for path in paths if not source.exists(path)]
            if missing:
                raise SnapshotError(
                    f"missing {kind} file(s): {', '.join(missing)}"
                )
        else:
            discovered = []
            for pattern in patterns:
                discovered.extend(source.list_files(pattern))
            paths = tuple(sorted(set(discovered)))

        if not paths:
            raise SnapshotError(f"no {kind} files found in the selected revision")
        return paths

    def build(
        self,
        source: FileSource,
        revision: ResolvedRevision,
        *,
        schema_paths: Optional[Sequence[str]] = None,
        data_paths: Optional[Sequence[str]] = None,
    ) -> OksSnapshot:
        if revision.repository != getattr(source, "repository", revision.repository):
            raise SnapshotError(
                "source repository does not match the resolved revision repository"
            )

        resolved_schema_paths = self._explicit_or_discovered(
            source, schema_paths, self.patterns.schema, "schema"
        )
        resolved_data_paths = self._explicit_or_discovered(
            source, data_paths, self.patterns.data, "data"
        )
        return OksSnapshot(
            revision=revision,
            schema_paths=resolved_schema_paths,
            data_paths=resolved_data_paths,
            source=source,
        )
