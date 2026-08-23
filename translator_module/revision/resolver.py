"""Resolve user revision requests to immutable Git commit metadata."""

from datetime import datetime
from pathlib import Path
import subprocess
from typing import Sequence

from .models import ResolvedRevision, RevisionRequest


class RevisionResolutionError(RuntimeError):
    """Raised when a requested Git revision cannot be resolved safely."""


class GitRevisionResolver:
    """Resolve commit, tag, date, and current revision requests.

    Run-ID resolution deliberately remains disabled until an explicit
    run-to-commit registry is supplied. A run number must never be guessed
    from a commit message or an approximate timestamp.
    """

    def __init__(self, repository: Path | str):
        repository_path = Path(repository).expanduser().resolve()
        if not repository_path.is_dir():
            raise RevisionResolutionError(
                f"repository is not a directory: {repository_path}"
            )
        self.repository = repository_path

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
            raise RevisionResolutionError(
                "Git executable was not found on PATH"
            ) from exc

        if check and result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise RevisionResolutionError(
                f"Git command failed for repository {self.repository}: "
                f"{' '.join(command)}\n{detail}"
            )
        return result

    def _resolve_commit(self, revision: str) -> str:
        if not revision or any(character.isspace() for character in revision):
            raise RevisionResolutionError(
                "revision must be a non-empty value without whitespace"
            )
        if revision.startswith("-"):
            raise RevisionResolutionError("revision must not start with '-'")

        result = self._run_git(
            ["rev-parse", "--verify", f"{revision}^{{commit}}"]
        )
        commit = result.stdout.decode("ascii", errors="replace").strip()
        if not commit:
            raise RevisionResolutionError(f"Git returned no commit for {revision!r}")
        return commit

    def _commit_date(self, commit: str) -> datetime:
        result = self._run_git(["show", "-s", "--format=%cI", commit])
        value = result.stdout.decode("ascii", errors="replace").strip()
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise RevisionResolutionError(
                f"Git returned an invalid commit date for {commit}: {value!r}"
            ) from exc

    def resolve(self, request: RevisionRequest | None = None) -> ResolvedRevision:
        """Resolve one request without changing the repository working tree."""

        request = request or RevisionRequest()
        selectors = [
            ("commit", request.commit_hash),
            ("tag", request.tag),
            ("date", request.date),
            ("run_id", request.run_id),
        ]
        selected = [(name, value) for name, value in selectors if value is not None]
        if len(selected) > 1:
            names = ", ".join(name for name, _ in selected)
            raise RevisionResolutionError(
                f"revision selectors are mutually exclusive; received: {names}"
            )

        if request.run_id is not None:
            raise RevisionResolutionError(
                "run_id cannot be resolved until a run-to-commit registry is configured"
            )

        if request.date is not None:
            if request.date.tzinfo is None or request.date.utcoffset() is None:
                raise RevisionResolutionError(
                    "date must be timezone-aware; use an ISO 8601 offset"
                )
            if not request.ref or request.ref.startswith("-"):
                raise RevisionResolutionError("ref must be a non-empty Git ref")

            before = request.date.isoformat()
            result = self._run_git(
                ["rev-list", "-1", f"--before={before}", request.ref],
                check=False,
            )
            if result.returncode != 0:
                detail = result.stderr.decode("utf-8", errors="replace").strip()
                raise RevisionResolutionError(
                    f"could not resolve date on ref {request.ref!r}: {detail}"
                )
            revision = result.stdout.decode("ascii", errors="replace").strip()
            if not revision:
                raise RevisionResolutionError(
                    f"no commit exists on ref {request.ref!r} at or before {before}"
                )
            commit = self._resolve_commit(revision)
            requested_as = "date"
        elif request.commit_hash is not None:
            commit = self._resolve_commit(request.commit_hash)
            requested_as = "commit"
        elif request.tag is not None:
            commit = self._resolve_commit(request.tag)
            requested_as = "tag"
        else:
            commit = self._resolve_commit("HEAD")
            requested_as = "current"

        return ResolvedRevision(
            repository=self.repository,
            commit=commit,
            requested_as=requested_as,
            ref=request.ref,
            commit_date=self._commit_date(commit),
        )
