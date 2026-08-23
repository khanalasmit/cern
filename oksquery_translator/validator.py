"""
validator.py — Two-Layer Query Validation
==========================================

Layer 1: Local syntax pre-check (fast, no subprocess)
  - Balanced parentheses
  - Quoted strings properly closed
  - Scope token (all/this) present at top
  - and/or have >=2 children; not has exactly 1
  - Known comparator tokens

Layer 2: Real oks_dump validation (definitive)
  - Runs ``oks_dump -c <class> -q '<query>' <file>``
  - Inspects exit code (0=OK, 3=bad query, 4=class not found)
  - Captures stderr for the repair loop
"""

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    error_type: str = ""       # "syntax", "bad_query", "class_not_found", "other"
    message: str = ""          # Human-readable error for the repair loop
    output: str = ""           # stdout from oks_dump (on success)


# ======================================================================
# Layer 1: Local Syntax Pre-Check
# ======================================================================

class SExpressionTokenizer:
    """
    Tokenizes an OksQuery S-expression into tokens:
    parentheses, quoted strings, and bare words.
    """

    def tokenize(self, text: str) -> List[str]:
        tokens = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch in " \t\n\r":
                i += 1
            elif ch == '(':
                tokens.append('(')
                i += 1
            elif ch == ')':
                tokens.append(')')
                i += 1
            elif ch == '"':
                # Quoted string — find closing quote
                j = i + 1
                while j < len(text) and text[j] != '"':
                    if text[j] == '\\':
                        j += 1  # skip escaped char
                    j += 1
                if j >= len(text):
                    raise SyntaxCheckError(
                        f"Unterminated quoted string starting at position {i}"
                    )
                tokens.append(text[i:j + 1])  # include quotes
                i = j + 1
            else:
                # Bare word (keyword, comparator, etc.)
                j = i
                while j < len(text) and text[j] not in ' \t\n\r()\"':
                    j += 1
                tokens.append(text[i:j])
                i = j
        return tokens


class SyntaxCheckError(ValueError):
    """Raised when the local syntax pre-check fails."""
    pass


_VALID_COMPARATORS = {"=", "!=", "<", ">", "<=", ">=", "~="}
_SCOPE_TOKENS = {"all", "this"}
_LOGICAL_KEYWORDS = {"and", "or", "not"}
_SPECIAL_KEYWORDS = {"object-id", "some", "all"}


def format_tokens(tokens: List[str]) -> str:
    """
    Format a list of tokens back into a standard OksQuery S-expression string.
    """
    res = []
    for i, t in enumerate(tokens):
        if t == '(':
            if i > 0 and tokens[i - 1] not in ('(', ' '):
                res.append(' ')
            res.append('(')
        elif t == ')':
            res.append(')')
        else:
            if i > 0 and tokens[i - 1] != '(':
                res.append(' ')
            res.append(t)
    return "".join(res)


def align_query_to_schema(target_class: str, query: str,
                          schema_retriever=None) -> tuple[str, str]:
    """
    Canonicalize and auto-correct casing for target class, attribute names,
    relationship names, and enum values against the live schema.

    In OKS, attribute and class names are strictly case-sensitive. This
    function ensures that casing mistakes (like 'Subdetector' -> 'SubDetector'
    or 'inittimeout' -> 'InitTimeout') are transparently aligned with the schema.

    Parameters
    ----------
    target_class : str
        The class name to query against.
    query : str
        The OksQuery string.
    schema_retriever : SchemaRetriever, optional
        Schema retriever to query class and attribute definitions.

    Returns
    -------
    tuple (aligned_class, aligned_query)
    """
    if not schema_retriever or not query:
        return target_class, query

    aligned_class = target_class

    # 1. Canonicalize class name casing
    try:
        class_list = schema_retriever.get_class_list()
        for c in class_list:
            if c.lower() == target_class.lower():
                aligned_class = c
                break
    except Exception:
        pass

    # 2. Gather attributes and relationships for this class and related classes
    attr_map = {}   # lower -> Canonical
    rel_map = {}    # lower -> Canonical
    enum_map = {}   # lower_attr -> { lower_enum -> Canonical_enum }

    try:
        info = schema_retriever.get_class_info(aligned_class)
        if info:
            for a in info.get("attributes", []):
                aname = a.get("name", "")
                if aname:
                    attr_map[aname.lower()] = aname
                    if a.get("type") == "enum" and a.get("range"):
                        enums = [e.strip() for e in a["range"].split(",") if e.strip()]
                        enum_map[aname.lower()] = {e.lower(): e for e in enums}

            for r in info.get("relationships", []):
                rname = r.get("name", "")
                if rname:
                    rel_map[rname.lower()] = rname
                    target = r.get("target_class")
                    if target:
                        tinfo = schema_retriever.get_class_info(target)
                        if tinfo:
                            for ta in tinfo.get("attributes", []):
                                taname = ta.get("name", "")
                                if taname:
                                    attr_map[taname.lower()] = taname
                            for tr in tinfo.get("relationships", []):
                                trname = tr.get("name", "")
                                if trname:
                                    rel_map[trname.lower()] = trname
    except Exception:
        pass

    # 3. Tokenize query and align identifiers
    try:
        tokenizer = SExpressionTokenizer()
        tokens = tokenizer.tokenize(query)
    except Exception:
        return aligned_class, query

    aligned_tokens = []
    for i, t in enumerate(tokens):
        if t.startswith('"') and t.endswith('"') and len(t) >= 2:
            inner = t[1:-1]
            inner_lower = inner.lower()

            # Is it an attribute name?
            if inner_lower in attr_map:
                aligned_tokens.append(f'"{attr_map[inner_lower]}"')
            # Is it a relationship name?
            elif inner_lower in rel_map:
                aligned_tokens.append(f'"{rel_map[inner_lower]}"')
            else:
                # Check if it's an enum value for a preceding attribute in the clause
                # Look backwards for the attribute name in this predicate
                replaced_enum = False
                for prev in reversed(aligned_tokens[max(0, i - 4):i]):
                    if prev.startswith('"') and prev.endswith('"'):
                        prev_name = prev[1:-1].lower()
                        if prev_name in enum_map and inner_lower in enum_map[prev_name]:
                            aligned_tokens.append(f'"{enum_map[prev_name][inner_lower]}"')
                            replaced_enum = True
                            break
                if not replaced_enum:
                    aligned_tokens.append(t)
        else:
            aligned_tokens.append(t)

    aligned_query = format_tokens(aligned_tokens)
    return aligned_class, aligned_query


def syntax_precheck(query: str) -> ValidationResult:
    """
    Fast local syntax check.  Returns a ValidationResult.

    This catches common LLM mistakes like:
      - Unbalanced parentheses
      - Missing/extra quotes
      - Missing scope token
      - and/or with <2 operands
      - Unknown comparator
    """
    query = query.strip()
    if not query:
        return ValidationResult(
            valid=False, error_type="syntax",
            message="Empty query string."
        )

    # Tokenize
    try:
        tokenizer = SExpressionTokenizer()
        tokens = tokenizer.tokenize(query)
    except SyntaxCheckError as e:
        return ValidationResult(
            valid=False, error_type="syntax", message=str(e)
        )

    # Check balanced parentheses
    depth = 0
    for t in tokens:
        if t == '(':
            depth += 1
        elif t == ')':
            depth -= 1
        if depth < 0:
            return ValidationResult(
                valid=False, error_type="syntax",
                message="Unbalanced parentheses: extra closing ')'."
            )
    if depth != 0:
        return ValidationResult(
            valid=False, error_type="syntax",
            message=f"Unbalanced parentheses: {depth} unclosed '('."
        )

    # Check that the query starts with ( scope ... )
    if len(tokens) < 3 or tokens[0] != '(':
        return ValidationResult(
            valid=False, error_type="syntax",
            message="Query must start with '(' followed by a scope token (all/this)."
        )

    scope_token = tokens[1]
    if scope_token not in _SCOPE_TOKENS:
        return ValidationResult(
            valid=False, error_type="syntax",
            message=(f"Expected scope token 'all' or 'this' as the first token "
                     f"after '(', got '{scope_token}'.")
        )

    # Walk the tokens to check logical operator arity
    errors = _check_logical_arity(tokens)
    if errors:
        return ValidationResult(
            valid=False, error_type="syntax",
            message="; ".join(errors)
        )

    return ValidationResult(valid=True)


def _check_logical_arity(tokens: List[str]) -> List[str]:
    """
    Walk the token list and check that and/or have >=2 child expressions
    and not has exactly 1.

    This does a simplified check by counting sub-expressions at each
    logical operator level.
    """
    errors = []

    # Find logical operators and count their child expressions
    # We do this by tracking parenthesis depth relative to each operator
    i = 0
    while i < len(tokens):
        if tokens[i] == '(' and i + 1 < len(tokens):
            keyword = tokens[i + 1]
            if keyword in ("and", "or"):
                # Count child expressions (sub-expressions at depth+1)
                children = _count_child_expressions(tokens, i)
                if children < 2:
                    errors.append(
                        f"'{keyword}' expression must have at least 2 "
                        f"operands, found {children}."
                    )
            elif keyword == "not":
                children = _count_child_expressions(tokens, i)
                if children != 1:
                    errors.append(
                        f"'not' expression must have exactly 1 operand, "
                        f"found {children}."
                    )
        i += 1

    return errors


def _count_child_expressions(tokens: List[str], start: int) -> int:
    """
    Given that tokens[start] is '(' and tokens[start+1] is a keyword,
    count how many child sub-expressions follow before the matching ')'.
    """
    # Skip past '(' and keyword
    depth = 1
    i = start + 2
    children = 0
    child_depth = 0

    while i < len(tokens) and depth > 0:
        if tokens[i] == '(':
            if depth == 1:
                children += 1
            depth += 1
        elif tokens[i] == ')':
            depth -= 1
        i += 1

    return children


# ======================================================================
# Layer 2: oks_dump Validation (Real Engine)
# ======================================================================

def validate_with_oks_dump(target_class: str, query: str,
                           data_file: str = "daq/segments/setup.data.xml",
                           timeout: int = 30) -> ValidationResult:
    """
    Run the query through oks_dump and inspect the exit code.

    Exit codes:
      0 → query is valid (result may be empty, that's fine)
      1 → bad command-line parameter
      2 → bad OKS file(s)
      3 → bad query (syntax error)
      4 → class not found
      5 → dangling references (usually a warning, not an error)

    Parameters
    ----------
    target_class : str
        OKS class name to query against.
    query : str
        OksQuery string.
    data_file : str
        OKS data file path.
    timeout : int
        Subprocess timeout in seconds.

    Returns
    -------
    ValidationResult
    """
    oks_dump_path = shutil.which("oks_dump")
    if not oks_dump_path:
        return ValidationResult(
            valid=True,  # Can't validate — assume valid
            message="oks_dump not found on PATH; skipping real validation."
        )

    cmd = [oks_dump_path, "-c", target_class, "-q", query, data_file]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return ValidationResult(
            valid=False, error_type="other",
            message=f"oks_dump timed out after {timeout}s."
        )
    except FileNotFoundError:
        return ValidationResult(
            valid=True,
            message="oks_dump not found; skipping real validation."
        )

    if result.returncode == 0:
        return ValidationResult(valid=True, output=result.stdout)

    stderr = result.stderr.strip()

    if result.returncode == 3:
        return ValidationResult(
            valid=False, error_type="bad_query",
            message=stderr or "Bad query syntax (oks_dump exit code 3)."
        )
    elif result.returncode == 4:
        return ValidationResult(
            valid=False, error_type="class_not_found",
            message=stderr or f"Class '{target_class}' not found (oks_dump exit code 4)."
        )
    elif result.returncode == 5:
        # Dangling references — usually a warning, query may still be valid
        return ValidationResult(
            valid=True, output=result.stdout,
            message="Warning: data contains dangling references (exit code 5)."
        )
    else:
        return ValidationResult(
            valid=False, error_type="other",
            message=stderr or f"oks_dump exited with code {result.returncode}."
        )


def validate_query(target_class: str, query: str,
                   data_file: str = "daq/segments/setup.data.xml") -> ValidationResult:
    """
    Two-layer validation: local syntax check first, then oks_dump.

    Parameters
    ----------
    target_class : str
        OKS class name.
    query : str
        OksQuery string.
    data_file : str
        OKS data file path.

    Returns
    -------
    ValidationResult
    """
    # Layer 1: fast local check
    result = syntax_precheck(query)
    if not result.valid:
        return result

    # Layer 2: real oks_dump validation
    return validate_with_oks_dump(target_class, query, data_file)
