"""Conservative schema checks before executing a historical query."""

from dataclasses import dataclass

from translator_module.rag.schema_loader import SchemaLoader
from translator_module.revision.models import OksSnapshot


class SchemaPreflightError(ValueError):
    """Raised when execution targets a class absent from the selected schema."""


@dataclass(frozen=True)
class SchemaPreflightResult:
    """The validated execution target and its source revision."""

    revision: str
    target_class: str
    schema_paths: tuple[str, ...]


class HistoricalSchemaPreflight:
    """Validate only facts that can be established safely from OKS XML.

    This intentionally checks target-class existence but does not reject
    attributes or relationships that are not declared directly on the class.
    OKS schemas may provide those members through inheritance, and resolving
    the complete inheritance graph belongs to the native OKS runtime.
    """

    @staticmethod
    def validate(snapshot: OksSnapshot, target_class: str) -> SchemaPreflightResult:
        normalized_target = (target_class or "").strip()
        if not normalized_target:
            raise SchemaPreflightError(
                "historical execution requires a non-empty target class"
            )
        if snapshot.source is None:
            raise SchemaPreflightError(
                "historical schema preflight requires a source-backed snapshot"
            )

        documents = SchemaLoader.load_source(
            snapshot.source,
            snapshot.schema_paths,
        )
        available_classes = {
            class_element.get("name")
            for document in documents
            for class_element in document.root.findall(".//class")
            if class_element.get("name")
        }
        if normalized_target not in available_classes:
            sample = ", ".join(sorted(available_classes)[:10])
            suffix = f" Available classes include: {sample}." if sample else ""
            raise SchemaPreflightError(
                f"target class {normalized_target!r} is not present in historical "
                f"revision {snapshot.revision.commit}.{suffix}"
            )

        return SchemaPreflightResult(
            revision=snapshot.revision.commit,
            target_class=normalized_target,
            schema_paths=tuple(snapshot.schema_paths),
        )
