"""Parse historical OKS data XML without choosing an execution engine."""

from dataclasses import dataclass
import xml.etree.ElementTree as ET
from typing import Iterable, List

from translator_module.revision.source import FileSource


class DataLoadError(ValueError):
    """Raised when historical OKS data cannot be parsed."""


@dataclass(frozen=True)
class DataDocument:
    source_path: str
    root: ET.Element


class HistoricalDataLoader:
    """Load standalone or embedded OKS data XML through a ``FileSource``."""

    @staticmethod
    def load_bytes(data: bytes, source_path: str) -> List[DataDocument]:
        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            raise DataLoadError(
                f"could not parse data XML {source_path}: "
                f"line {exc.position[0]}, column {exc.position[1]}: {exc}"
            ) from exc

        embedded = root.findall(".//data-file")
        if not embedded:
            return [DataDocument(source_path=source_path, root=root)]

        documents = []
        for index, data_file in enumerate(embedded):
            data_text = "".join(data_file.itertext()).strip()
            if not data_text:
                continue
            name = data_file.get("name") or f"embedded-data-{index}"
            embedded_path = f"{source_path}::{name}"
            try:
                embedded_root = ET.fromstring(data_text)
            except ET.ParseError as exc:
                raise DataLoadError(
                    f"could not parse embedded data XML {embedded_path}: "
                    f"line {exc.position[0]}, column {exc.position[1]}: {exc}"
                ) from exc
            documents.append(
                DataDocument(source_path=embedded_path, root=embedded_root)
            )
        return documents

    @classmethod
    def load_source(
        cls,
        source: FileSource,
        paths: Iterable[str],
    ) -> List[DataDocument]:
        documents = []
        for path in paths:
            documents.extend(cls.load_bytes(source.read_bytes(path), path))
        return documents
