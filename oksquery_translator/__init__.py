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

# Core pipeline
from .pipeline import OksPipeline, answer

# Intent classification & run resolution
from .intent import Intent, IntentResult, IntentClassifier, extract_run_and_partition, RunResolver

# Execution layer (preserved, battle-tested)
from .executor import Executor, ExecutionResult

# Context (Module 1 & 2)
from .context import OksContext, compute_fingerprint, OksContextBuilder

# Query preprocessing (Module 3)
from .preprocessing import QueryPreprocessor, QueryAnalysis

# Schema provider (Module 5)
from .schema import OksSchemaProvider, ClassDefinition, AttributeDefinition, RelationshipDefinition

# AST models, normalizer, validator, compiler (Modules 9, 10, 11, 12)
from .ast import (
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

# Schema search index (Module 4)
from .retrieval import SchemaSearchIndex, ClassSearchDocument

__all__ = [
    # Pipeline
    "OksPipeline",
    "answer",
    # Intent
    "Intent",
    "IntentResult",
    "IntentClassifier",
    "extract_run_and_partition",
    "RunResolver",
    # Executor (unchanged)
    "Executor",
    "ExecutionResult",
    # Context
    "OksContext",
    "compute_fingerprint",
    "OksContextBuilder",
    # Preprocessing
    "QueryPreprocessor",
    "QueryAnalysis",
    # Schema
    "OksSchemaProvider",
    "ClassDefinition",
    "AttributeDefinition",
    "RelationshipDefinition",
    # AST
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
    # Retrieval index
    "SchemaSearchIndex",
    "ClassSearchDocument",
]
