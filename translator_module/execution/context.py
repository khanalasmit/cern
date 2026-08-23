"""Immutable context passed to a future historical OKS executor."""

from dataclasses import dataclass
from typing import Optional

from translator_module.revision.models import OksSnapshot
from .data_loader import DataDocument, HistoricalDataLoader


class ExecutionContextError(ValueError):
    """Raised when a historical execution context is incomplete."""


@dataclass(frozen=True)
class HistoricalExecutionContext:
    """Bind one serialized query to one consistent historical snapshot."""

    snapshot: OksSnapshot
    oks_query: str
    target_class: Optional[str] = None

    def load_data(self) -> list[DataDocument]:
        if self.snapshot.source is None:
            raise ExecutionContextError(
                "historical execution requires a source-backed snapshot"
            )
        return HistoricalDataLoader.load_source(
            self.snapshot.source,
            self.snapshot.data_paths,
        )
