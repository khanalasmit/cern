"""Explicit mapping between domain run IDs and Git revisions."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Optional


class RunRegistryError(ValueError):
    """Raised when a run-to-commit registry is missing or invalid."""


@dataclass(frozen=True)
class RunRevision:
    """The Git revision metadata registered for one domain run."""

    run_id: str
    commit: str
    timestamp: Optional[str] = None


class RunRevisionRegistry:
    """Read and query an explicit JSON run-to-commit mapping."""

    def __init__(self, entries: Mapping[str, RunRevision]):
        self._entries = dict(entries)

    @classmethod
    def from_json(cls, path: Path | str) -> "RunRevisionRegistry":
        registry_path = Path(path).expanduser().resolve()
        if not registry_path.is_file():
            raise RunRegistryError(f"run registry file does not exist: {registry_path}")

        try:
            with registry_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise RunRegistryError(
                f"run registry is not valid JSON: {registry_path}: {exc}"
            ) from exc
        except OSError as exc:
            raise RunRegistryError(
                f"could not read run registry: {registry_path}: {exc}"
            ) from exc

        return cls.from_mapping(payload, source=str(registry_path))

    @classmethod
    def from_mapping(
        cls,
        payload: Any,
        *,
        source: str = "run registry",
    ) -> "RunRevisionRegistry":
        if not isinstance(payload, dict):
            raise RunRegistryError(f"{source} must contain a JSON object")

        entries = {}
        for raw_run_id, raw_value in payload.items():
            run_id = str(raw_run_id).strip()
            if not run_id:
                raise RunRegistryError(f"{source} contains an empty run ID")

            if isinstance(raw_value, str):
                commit = raw_value
                timestamp = None
            elif isinstance(raw_value, dict):
                commit = raw_value.get("commit")
                timestamp = raw_value.get("timestamp")
            else:
                raise RunRegistryError(
                    f"{source} entry {run_id!r} must be a commit string or object"
                )

            if not isinstance(commit, str) or not commit.strip():
                raise RunRegistryError(
                    f"{source} entry {run_id!r} must contain a non-empty commit"
                )
            if any(character.isspace() for character in commit):
                raise RunRegistryError(
                    f"{source} entry {run_id!r} contains whitespace in its commit"
                )
            if timestamp is not None and not isinstance(timestamp, str):
                raise RunRegistryError(
                    f"{source} entry {run_id!r} has a non-string timestamp"
                )

            entries[run_id] = RunRevision(
                run_id=run_id,
                commit=commit.strip(),
                timestamp=timestamp,
            )

        return cls(entries)

    def resolve(self, run_id: str) -> RunRevision:
        key = str(run_id).strip()
        if not key:
            raise RunRegistryError("run ID must be non-empty")
        try:
            return self._entries[key]
        except KeyError as exc:
            raise RunRegistryError(
                f"run ID {key!r} is not present in the run registry"
            ) from exc

    @property
    def entries(self) -> Mapping[str, RunRevision]:
        """Return a read-only-style view of the loaded entries."""
        return self._entries.copy()
