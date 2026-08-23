"""Filesystem-like sources used by current and historical loaders."""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator, List
import ntpath


class FileSource(ABC):
    """Read-only interface shared by working-tree and Git-backed sources."""

    @abstractmethod
    def read_bytes(self, relative_path: str) -> bytes:
        """Return the exact bytes stored at a repository-relative path."""

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        """Return whether a repository-relative file exists."""

    @abstractmethod
    def list_files(self, pattern: str) -> List[str]:
        """Return matching repository-relative file paths in stable order."""

    def open_binary(self, relative_path: str) -> BinaryIO:
        """Expose file contents as a binary stream for XML parsers."""
        return BytesIO(self.read_bytes(relative_path))

    @abstractmethod
    def materialize(self) -> Iterator[Path]:
        """Yield a filesystem directory containing this source snapshot."""


def _validate_relative_path(relative_path: str) -> PurePosixPath:
    """Validate a Git-style relative path before it reaches the filesystem."""

    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("relative_path must be a non-empty string")

    normalized = relative_path.replace("\\", "/")
    if ntpath.isabs(relative_path) or PurePosixPath(normalized).is_absolute():
        raise ValueError(f"absolute paths are not allowed: {relative_path!r}")

    path = PurePosixPath(normalized)
    if ".." in path.parts:
        raise ValueError(f"parent-directory paths are not allowed: {relative_path!r}")

    return path


class WorkingTreeSource(FileSource):
    """Read files from a repository working tree without changing it."""

    def __init__(self, root: Path | str):
        root_path = Path(root).expanduser().resolve()
        if not root_path.is_dir():
            raise ValueError(f"source root is not a directory: {root_path}")
        self.root = root_path

    def _path(self, relative_path: str) -> Path:
        relative = _validate_relative_path(relative_path)
        candidate = (self.root / Path(*relative.parts)).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(
                f"path resolves outside source root: {relative_path!r}"
            ) from exc
        return candidate

    def read_bytes(self, relative_path: str) -> bytes:
        return self._path(relative_path).read_bytes()

    def exists(self, relative_path: str) -> bool:
        return self._path(relative_path).is_file()

    def list_files(self, pattern: str) -> List[str]:
        pattern_path = _validate_relative_path(pattern)
        matches = []
        for candidate in self.root.glob(pattern_path.as_posix()):
            if candidate.is_file():
                resolved = candidate.resolve()
                try:
                    relative = resolved.relative_to(self.root)
                except ValueError as exc:
                    raise ValueError(
                        f"pattern resolves outside source root: {pattern!r}"
                    ) from exc
                matches.append(relative.as_posix())
        return sorted(matches)

    @contextmanager
    def materialize(self) -> Iterator[Path]:
        """Yield the existing working-tree root without changing it."""
        yield self.root
