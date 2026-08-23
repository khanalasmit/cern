"""Adapter boundary for executing a query against a historical snapshot."""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from translator_module.revision.models import OksSnapshot
from .context import HistoricalExecutionContext


class OksExecutionError(RuntimeError):
    """Raised when no usable historical OKS execution backend is available."""


class OksExecutionBackend(Protocol):
    """Interface implemented by the native OKS runtime adapter."""

    def execute(
        self,
        *,
        snapshot: OksSnapshot,
        oks_query: str,
        target_class: str,
    ) -> Sequence[Mapping[str, Any]]:
        """Execute against exactly the supplied historical snapshot."""


@dataclass(frozen=True)
class ExecutionResult:
    revision: str
    target_class: str
    rows: tuple[Mapping[str, Any], ...]


class HistoricalOksExecutor:
    """Run historical queries through an injected native OKS backend."""

    def __init__(self, backend: OksExecutionBackend | None = None):
        self.backend = backend

    def execute(self, context: HistoricalExecutionContext) -> ExecutionResult:
        if self.backend is None:
            raise OksExecutionError(
                "no native OKS execution backend is configured"
            )
        target_class = context.require_target_class()
        if context.snapshot.source is None:
            raise OksExecutionError(
                "historical execution requires a source-backed snapshot"
            )

        rows = self.backend.execute(
            snapshot=context.snapshot,
            oks_query=context.oks_query,
            target_class=target_class,
        )
        return ExecutionResult(
            revision=context.snapshot.revision.commit,
            target_class=target_class,
            rows=tuple(rows),
        )
