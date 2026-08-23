"""Read-only access to files stored in a Git revision."""

from pathlib import Path, PurePosixPath
import subprocess
from typing import List, Sequence

from .source import FileSource, _validate_relative_path


class GitSourceError(RuntimeError):
    """Raised when a historical Git source cannot read its repository data."""


class GitRevisionSource(FileSource):
    """Expose one Git commit as a read-only ``FileSource``.

    The source uses Git object access commands only. It never checks out,
    resets, updates, or otherwise changes the repository working tree.
    """

    def __init__(self, repository: Path | str, commit: str):
        repository_path = Path(repository).expanduser().resolve()
        if not repository_path.is_dir():
            raise GitSourceError(f"repository is not a directory: {repository_path}")
        if not commit or any(character.isspace() for character in commit):
            raise GitSourceError("commit must be a non-empty revision without whitespace")
        if commit.startswith("-"):
            raise GitSourceError("commit must not start with '-'")

        self.repository = repository_path
        self.commit = self._resolve_commit(commit)

    def _run_git(
        self,
        arguments: Sequence[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        command = ["git", "-C", str(self.repository), *arguments]
        try:
            result = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise GitSourceError("Git executable was not found on PATH") from exc

        if check and result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise GitSourceError(
                f"Git command failed for repository {self.repository}: "
                f"{' '.join(command)}\n{detail}"
            )
        return result

    def _resolve_commit(self, revision: str) -> str:
        result = self._run_git(
            ["rev-parse", "--verify", f"{revision}^{{commit}}"]
        )
        commit = result.stdout.decode("ascii", errors="replace").strip()
        if not commit:
            raise GitSourceError(f"Git returned an empty commit for {revision!r}")
        return commit

    def _object_spec(self, relative_path: str) -> str:
        path = _validate_relative_path(relative_path)
        return f"{self.commit}:{path.as_posix()}"

    def read_bytes(self, relative_path: str) -> bytes:
        """Read one historical blob using ``git show``."""

        path = _validate_relative_path(relative_path)
        result = self._run_git(
            ["show", "--no-ext-diff", "--format=", self._object_spec(path.as_posix())]
        )
        return result.stdout

    def exists(self, relative_path: str) -> bool:
        """Return true only when the historical path resolves to a blob."""

        object_spec = self._object_spec(relative_path)
        result = self._run_git(["cat-file", "-t", object_spec], check=False)
        if result.returncode != 0:
            return False
        return result.stdout.decode("ascii", errors="replace").strip() == "blob"

    def list_files(self, pattern: str) -> List[str]:
        """List historical files matching working-tree-style glob syntax."""

        pathspec = _validate_relative_path(pattern).as_posix()
        result = self._run_git(
            ["ls-tree", "-r", "--name-only", self.commit]
        )
        files = result.stdout.decode("utf-8", errors="strict").splitlines()
        return sorted(
            path
            for path in files
            if path and PurePosixPath(path).match(pathspec)
        )
