"""
context/oks_context.py — Immutable per-request OKS context
===========================================================

The OksContext is the single source of truth for a pipeline request.
Once built, it is passed unchanged to every downstream component:
  schema retrieval, prompt builder, AST validator, repair engine, compiler, executor.

No module may create a second OksContext or load a different schema version.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class OksContext:
    """
    Immutable context that binds a pipeline request to an exact OKS schema version.

    Fields
    ------
    schema_identifier : str
        Human-readable schema label (e.g. "tdaq-13-00-00", "run-380689", or "current").
    schema_fingerprint : str
        A short hash derived from sorted class names in this resolved schema.
        This is the version key used to scope all retrieval index lookups and validation.
    release : Optional[str]
        TDAQ release string, e.g. "tdaq-13-00-00". None for current/HEAD.
    git_revision : Optional[str]
        Full git commit SHA of the OKS configuration repo. None for HEAD.
    run_number : Optional[int]
        ATLAS experiment run number (e.g. 380689). None for current.
    configuration_revision : Optional[str]
        Configuration revision string from the run database.
    version_tag : Optional[str]
        The resolved version tag string, e.g. "tag:r380689@all_hosts" or None.
    """

    schema_identifier: str
    schema_fingerprint: str
    release: Optional[str] = None
    git_revision: Optional[str] = None
    run_number: Optional[int] = None
    configuration_revision: Optional[str] = None
    version_tag: Optional[str] = None

    @property
    def is_current(self) -> bool:
        """True if this context refers to the current/HEAD configuration."""
        return (
            self.git_revision is None
            and self.run_number is None
            and self.release is None
            and self.version_tag is None
        )

    @property
    def display_label(self) -> str:
        """Human-readable label for logging and user-facing headers."""
        if self.run_number is not None:
            return f"Run {self.run_number} ({self.schema_identifier})"
        if self.release:
            return self.release
        if self.version_tag:
            return self.version_tag
        return "Current / Default (HEAD)"

    def to_prompt_metadata(self) -> str:
        """
        Returns a short metadata block to embed in LLM prompts (Module 7, Component C).
        This tells the LLM exactly which schema context it is operating in.
        """
        lines = [
            "=== OksContext Metadata ===",
            f"Schema identifier   : {self.schema_identifier}",
            f"Schema fingerprint  : {self.schema_fingerprint}",
        ]
        if self.git_revision:
            lines.append(f"Git revision        : {self.git_revision}")
        if self.run_number is not None:
            lines.append(f"Run number          : {self.run_number}")
        if self.configuration_revision:
            lines.append(f"Configuration rev   : {self.configuration_revision}")
        if self.version_tag:
            lines.append(f"Version tag         : {self.version_tag}")
        lines.append(
            "IMPORTANT: Only schema terms valid in this exact fingerprint are authoritative."
        )
        lines.append("=== End OksContext Metadata ===")
        return "\n".join(lines)


def compute_fingerprint(class_names: Iterable[str]) -> str:
    """
    Compute a short, stable schema fingerprint from a collection of class names.

    The fingerprint is a 16-character hex prefix of the SHA-256 of all
    unique class names joined by '|' in sorted alphabetical order.

    This is used as the retrieval index key to ensure retrieval documents
    are only served to requests using the same exact schema version.
    """
    sorted_names = sorted(set(class_names))
    payload = "|".join(sorted_names).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]
