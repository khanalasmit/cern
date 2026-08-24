"""Stateless service facade used by the MCP adapter.

The service deliberately owns the safe, server-side configuration while the
agent that calls MCP owns conversation history and follow-up resolution.
"""

from __future__ import annotations

import os
import re
import threading
from typing import Any, Dict, Optional

from .pipeline import OksPipeline


class ServiceInputError(ValueError):
    """Raised when an MCP request violates the service input contract."""


class OksQueryService:
    """Expose a bounded, stateless OKS query capability."""

    def __init__(self, pipeline: Optional[OksPipeline] = None,
                 *, repo_root: Optional[str] = None,
                 data_file: Optional[str] = None,
                 schema_dir: Optional[str] = None,
                 max_question_chars: int = 4000,
                 max_version_chars: int = 160,
                 max_results: int = 200):
        if max_question_chars < 1 or max_version_chars < 1 or max_results < 1:
            raise ValueError("service limits must be positive")

        self.max_question_chars = max_question_chars
        self.max_version_chars = max_version_chars
        self.max_results = max_results
        # Executor/context version selection temporarily touches TDAQ
        # environment variables. Serialize requests so a future HTTP
        # transport cannot cross-contaminate concurrent versioned queries.
        self._pipeline_lock = threading.RLock()
        self.repo_root = repo_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        self.data_file = data_file or os.environ.get(
            "OKS_DATA_FILE", "daq/segments/setup.data.xml"
        )
        self.schema_dir = schema_dir or os.environ.get("OKS_SCHEMA_DIR")

        # Dependency injection keeps the service cheap and deterministic in
        # tests, while normal startup creates the existing pipeline once.
        self.pipeline = pipeline or OksPipeline(
            repo_root=self.repo_root,
            data_file=self.data_file,
            schema_dir=self.schema_dir,
            max_retries=int(os.environ.get("OKS_MAX_RETRIES", "3")),
        )

    def query(self, question: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Translate and execute one complete, self-contained question."""
        self._validate_question(question)
        self._validate_version(version)

        with self._pipeline_lock:
            result = self.pipeline.answer(question, version=version, interpret=False)
        return self._normalize_result(result)

    def translate(self, question: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Translate one question without executing it."""
        self._validate_question(question)
        self._validate_version(version)
        with self._pipeline_lock:
            result = self.pipeline.translate_only(question, version=version)
        normalized = dict(result)
        normalized.setdefault("warnings", [])
        normalized["results"] = []
        normalized["result_count"] = 0
        normalized["version"] = version or "current"
        return normalized

    def environment_probe(self) -> Dict[str, Any]:
        """Return non-secret runtime readiness information."""
        with self._pipeline_lock:
            probe = self.pipeline.schema_retriever.environment_probe()
        return {
            "status": "success",
            "data_file": self.data_file,
            "schema_dir": self.schema_dir or probe.get("schema_dir"),
            "oks_dump": probe.get("oks_dump", "NOT FOUND"),
            "config_module": probe.get("config_module", "NOT available"),
            "oks_dump_status": probe.get("oks_dump_status", "unknown"),
            "class_count": probe.get("class_count", 0),
            "classes": probe.get("classes", []),
        }

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        results = result.get("results") or []
        warnings = list(result.get("warnings") or [])
        if len(results) > self.max_results:
            results = results[:self.max_results]
            warnings.append(
                f"Results were capped at {self.max_results}; "
                "use a narrower question for the complete set."
            )

        normalized = {
            "status": result.get("status", "error"),
            "answer": result.get("answer", ""),
            "message": result.get("message", ""),
            "target_class": result.get("target_class", ""),
            "oks_query": result.get("oks_query", ""),
            "result_count": result.get("result_count", len(results)),
            "results": results,
            "attempts": result.get("attempts", 0),
            "version": result.get("version", "current"),
            "version_used": result.get("version_used", "current"),
            "intent": result.get("intent", ""),
            "run_number": result.get("run_number"),
            "partition": result.get("partition"),
            "schema_fingerprint": result.get("schema_fingerprint", ""),
            "oks_context_label": result.get("oks_context_label", ""),
            "ir": result.get("ir"),
            "warnings": warnings,
        }
        return normalized

    def _validate_question(self, question: str) -> None:
        if not isinstance(question, str):
            raise ServiceInputError("question must be a string")
        if not question.strip():
            raise ServiceInputError("question must not be empty")
        if len(question) > self.max_question_chars:
            raise ServiceInputError(
                f"question exceeds the {self.max_question_chars}-character limit"
            )

    def _validate_version(self, version: Optional[str]) -> None:
        if version is None:
            return
        if not isinstance(version, str):
            raise ServiceInputError("version must be a string or null")
        if len(version) > self.max_version_chars:
            raise ServiceInputError(
                f"version exceeds the {self.max_version_chars}-character limit"
            )
        if not version.strip():
            raise ServiceInputError("version must not be empty")
        # Versions are selectors, not filesystem paths. Keep the accepted
        # forms aligned with the existing pipeline's resolver/executor while
        # rejecting path separators and shell-like input.
        allowed = (
            r"hash:[A-Za-z0-9._-]+",
            r"date:[A-Za-z0-9:._+@-]+",
            r"tag:r\d+@[A-Za-z0-9._-]+",
            r"tdaq-\d{2}-\d{2}-\d{2}",
            r"run:\d+",
            r"r\d+",
        )
        if not any(re.fullmatch(pattern, version) for pattern in allowed):
            raise ServiceInputError(
                "unsupported version; use hash:, date:, tag:, tdaq-, or run:"
            )


def service_from_environment() -> OksQueryService:
    """Build the service from non-secret process configuration."""
    repo_root = os.environ.get("OKS_REPO_ROOT")
    data_file = os.environ.get("OKS_DATA_FILE")
    schema_dir = os.environ.get("OKS_SCHEMA_DIR")
    max_results = int(os.environ.get("OKS_MAX_RESULTS", "200"))
    return OksQueryService(
        repo_root=repo_root,
        data_file=data_file,
        schema_dir=schema_dir,
        max_results=max_results,
    )
