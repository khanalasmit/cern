"""Load scraped and standalone OKS schemas through a common interface."""

from dataclasses import dataclass
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, List

from translator_module.revision.source import FileSource


class SchemaLoadError(ValueError):
    """Raised when an OKS schema document cannot be parsed."""


@dataclass(frozen=True)
class SchemaDocument:
    """One parsed schema root and the source path it came from."""

    source_path: str
    root: ET.Element


class SchemaLoader:
    """Normalize supported OKS XML layouts into ``SchemaDocument`` objects."""

    @staticmethod
    def load_bytes(data: bytes, source_path: str) -> List[SchemaDocument]:
        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            raise SchemaLoadError(
                f"could not parse schema XML {source_path}: "
                f"line {exc.position[0]}, column {exc.position[1]}: {exc}"
            ) from exc

        embedded = root.findall(".//schema-file")
        if not embedded:
            return [SchemaDocument(source_path=source_path, root=root)]

        documents = []
        for index, schema_file in enumerate(embedded):
            schema_text = "".join(schema_file.itertext()).strip()
            if not schema_text:
                continue
            name = schema_file.get("name") or f"embedded-schema-{index}"
            embedded_path = f"{source_path}::{name}"
            try:
                embedded_root = ET.fromstring(schema_text)
            except ET.ParseError as exc:
                raise SchemaLoadError(
                    f"could not parse embedded schema XML {embedded_path}: "
                    f"line {exc.position[0]}, column {exc.position[1]}: {exc}"
                ) from exc
            documents.append(
                SchemaDocument(source_path=embedded_path, root=embedded_root)
            )

        return documents

    @classmethod
    def load_file(cls, path: Path | str) -> List[SchemaDocument]:
        file_path = Path(path)
        try:
            data = file_path.read_bytes()
        except OSError as exc:
            raise SchemaLoadError(f"could not read schema XML {file_path}: {exc}") from exc
        return cls.load_bytes(data, str(file_path))

    @classmethod
    def load_source(
        cls,
        source: FileSource,
        paths: Iterable[str],
    ) -> List[SchemaDocument]:
        documents = []
        for path in paths:
            documents.extend(cls.load_bytes(source.read_bytes(path), path))
        return documents
