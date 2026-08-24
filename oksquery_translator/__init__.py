"""
oksquery_translator — Text-to-OksQuery Translation Module
=========================================================

Translates natural-language questions about the ATLAS DAQ configuration
into valid OksQuery strings, executes them, and returns clean answers.

Runs on CERN lxplus with a sourced TDAQ release.

Usage::

    from oksquery_translator import answer, OksPipeline

    # Quick one-shot
    print(answer("Which test executables take longer than 2 seconds to initialise?"))

    # Full pipeline with options
    pipeline = OksPipeline()
    result = pipeline.answer("Which applications run on host lxplus001.cern.ch?")
    print(result["oks_query"])
    print(result["answer"])
"""

from .pipeline import OksPipeline, answer
from .intent import Intent, IntentResult, IntentClassifier, extract_run_and_partition, RunResolver
from .executor import Executor, ExecutionResult
from .context import OksContext, compute_fingerprint, OksContextBuilder
from .preprocessing import QueryPreprocessor, QueryAnalysis
from .schema import OksSchemaProvider, ClassDefinition, AttributeDefinition, RelationshipDefinition
from .oks_ast import (
    QueryIR,
    Expression,
    AttributeCompare,
    ObjectIdCompare,
    RelationshipCompare,
    AndExpression,
    OrExpression,
    NotExpression,
    ValidationResult,
    normalize_ir,
    NormalizerError,
    OksCompiler,
    serialize_ir_to_oks,
    ASTValidator,
)
from .retrieval import SchemaSearchIndex, ClassSearchDocument

__all__ = [
    "OksPipeline",
    "answer",
    "Intent",
    "IntentResult",
    "IntentClassifier",
    "extract_run_and_partition",
    "RunResolver",
    "Executor",
    "ExecutionResult",
    "OksContext",
    "compute_fingerprint",
    "OksContextBuilder",
    "QueryPreprocessor",
    "QueryAnalysis",
    "OksSchemaProvider",
    "ClassDefinition",
    "AttributeDefinition",
    "RelationshipDefinition",
    "QueryIR",
    "Expression",
    "AttributeCompare",
    "ObjectIdCompare",
    "RelationshipCompare",
    "AndExpression",
    "OrExpression",
    "NotExpression",
    "ValidationResult",
    "normalize_ir",
    "NormalizerError",
    "OksCompiler",
    "serialize_ir_to_oks",
    "ASTValidator",
    "SchemaSearchIndex",
    "ClassSearchDocument",
]
