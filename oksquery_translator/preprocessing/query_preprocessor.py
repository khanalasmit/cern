"""
preprocessing/query_preprocessor.py — Module 3: Query Preprocessor
=====================================================================

Analyzes a natural-language question deterministically (zero LLM calls) to extract:
  - Meaningful query tokens (lowercased, punctuation-cleaned, stop-words removed)
  - Candidate entity names (hostnames like lxplus001.cern.ch, quoted strings, object IDs)
  - Candidate OKS class hints mapped from domain vocabulary
  - Numeric constraint hints (operator + value + optional attribute hint)
  - Numeric values mentioned

The QueryAnalysis output feeds schema retrieval with prioritized entity & class hints.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

# OKS-domain stop words
_STOP_WORDS = {
    "which", "what", "where", "who", "how", "find", "show", "list", "get",
    "give", "tell", "does", "have", "has", "are", "is", "the", "a", "an",
    "of", "in", "on", "at", "to", "for", "with", "all", "any", "and", "or",
    "not", "that", "this", "these", "those", "me", "us", "my", "their",
    "oks", "query", "configuration", "database", "atlas", "tdaq",
}

# Comparison phrases to OKSQuery operator mapping
_COMPARATOR_MAP = {
    "greater than or equal to": ">=",
    "less than or equal to":    "<=",
    "greater than":             ">",
    "more than":                ">",
    "larger than":              ">",
    "exceeds":                  ">",
    "above":                    ">",
    "less than":                "<",
    "smaller than":             "<",
    "below":                    "<",
    "at least":                 ">=",
    "no less than":             ">=",
    "at most":                  "<=",
    "no more than":             "<=",
    "equal to":                 "=",
    "equals":                   "=",
    "exactly":                  "=",
    "not equal to":             "!=",
    "not equal":                "!=",
    "different from":           "!=",
    "matches":                  "~=",
    "like":                     "~=",
    "contains":                 "~=",
    "starts with":              "~=",
    ">=":                       ">=",
    "<=":                       "<=",
    "!=":                       "!=",
    "==":                       "=",
    "=":                        "=",
    ">":                        ">",
    "<":                        "<",
}

# Domain keyword to candidate OKS class mappings
_KEYWORD_TO_CLASS_HINTS = {
    "application":    ["Application", "BaseApplication", "RunControlApplication"],
    "applications":   ["Application", "BaseApplication", "RunControlApplication"],
    "executable":     ["Executable", "Binary"],
    "executables":    ["Executable", "Binary"],
    "binary":         ["Binary", "Executable"],
    "binaries":       ["Binary", "Executable"],
    "computer":       ["Computer"],
    "computers":      ["Computer"],
    "host":           ["Computer"],
    "hosts":          ["Computer"],
    "machine":        ["Computer"],
    "machines":       ["Computer"],
    "segment":        ["Segment", "OnlineSegment"],
    "segments":       ["Segment", "OnlineSegment"],
    "partition":      ["Partition"],
    "partitions":     ["Partition"],
    "resource":       ["Resource", "ResourceBase"],
    "resources":      ["Resource", "ResourceBase"],
    "timeout":        ["BaseApplication", "Executable"],
    "inittimeout":    ["BaseApplication", "Executable"],
    "exittimeout":    ["BaseApplication", "Executable"],
    "initialise":     ["BaseApplication", "Executable"],
    "initialize":     ["BaseApplication", "Executable"],
    "trigger":        ["DFTriggerIn"],
    "readout":        ["ROSDescriptor", "ReadoutApplication"],
    "ros":            ["ROSDescriptor"],
    "repository":     ["SW_Repository"],
    "software":       ["SW_Object", "ComputerProgram"],
    "program":        ["ComputerProgram"],
    "tag":            ["Tag"],
    "variable":       ["Variable", "VariableSet"],
    "parameter":      ["Parameter"],
    "parameters":     ["Parameter"],
    "rack":           ["Rack", "RackBase"],
    "test":           ["Test", "Test4Class", "Test4Object", "ExecutableTest"],
    "control":        ["RunControlApplication", "RunControlApplicationBase"],
    "controller":     ["RunControlApplication", "RunControlApplicationBase"],
    "run":            ["RunControlApplication"],
    "rc":             ["RunControlApplication", "RunControlApplicationBase"],
    "gatherer":       ["MIGApplication"],
    "monitoring":     ["MIGApplication", "MIGConfiguration"],
    "infrastructure": ["InfrastructureBase"],
    "ipc":            ["IPCServiceApplication"],
    "service":        ["IPCServiceApplication"],
    "corba":          ["IPCServiceApplication"],
    "container":      ["Container"],
    "element":        ["Element"],
    "failure":        ["TestFailure"],
}


@dataclass
class ConstraintHint:
    """Represents a detected constraint (operator and value) in natural language."""
    raw_text: str
    operator: str
    value: str
    attribute_hint: Optional[str] = None


@dataclass
class QueryAnalysis:
    """Structured analysis of a natural language question for OKS querying."""
    original_query: str
    normalized_query: str
    meaningful_tokens: List[str] = field(default_factory=list)
    candidate_entities: List[str] = field(default_factory=list)
    candidate_class_hints: List[str] = field(default_factory=list)
    constraint_hints: List[ConstraintHint] = field(default_factory=list)
    numeric_values: List[str] = field(default_factory=list)

    def to_retrieval_query(self) -> str:
        """
        Produce a prioritized, deduplicated token string for schema search.
        Class hints and meaningful tokens are placed first.
        """
        hints = list(self.candidate_class_hints) + self.meaningful_tokens
        seen = set()
        deduped = []
        for h in hints:
            h_clean = h.strip()
            if h_clean.lower() not in seen and len(h_clean) >= 2:
                seen.add(h_clean.lower())
                deduped.append(h_clean)
        return " ".join(deduped[:15]) or self.normalized_query


class QueryPreprocessor:
    """
    Deterministic NL question analyzer (Module 3).
    Extracts class hints, entities, constraints, and tokens without calling an LLM.
    """

    def analyze(self, question: str) -> QueryAnalysis:
        """
        Analyze the question and return a structured QueryAnalysis object.
        """
        q = question.strip() if question else ""
        normalized = " ".join(q.lower().split())

        # Extract tokens
        tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", q)
        meaningful = [
            t for t in tokens
            if t.lower() not in _STOP_WORDS and len(t) >= 2
        ]

        entities = self._extract_entities(q)
        class_hints = self._extract_class_hints(meaningful)
        constraints = self._extract_constraints(q)
        numerics = self._extract_numerics(q)

        return QueryAnalysis(
            original_query=q,
            normalized_query=normalized,
            meaningful_tokens=[t.lower() for t in meaningful],
            candidate_entities=entities,
            candidate_class_hints=class_hints,
            constraint_hints=constraints,
            numeric_values=numerics,
        )

    @staticmethod
    def _extract_entities(question: str) -> List[str]:
        """Extract quoted identifiers, hostnames/FQDNs, and camelCase object IDs."""
        entities: List[str] = []

        # 1. Quoted strings (e.g. 'pc01', "lxplus001.cern.ch")
        entities += re.findall(r'["\']([^"\']+)["\']', question)

        # 2. Hostnames / FQDNs (e.g. lxplus001.cern.ch, pc-tdaq-01)
        entities += re.findall(
            r'\b(?:[a-zA-Z][\w-]{1,}(?:\.[\w-]+){1,3})\b', question
        )

        # 3. Known host pattern prefixes (e.g. pc01, lxplus002, host1)
        entities += re.findall(
            r'\b(?:pc\d+|lxplus\d+|host\d+)\b', question, re.IGNORECASE
        )

        # Deduplicate while preserving original order
        return list(dict.fromkeys(entities))

    @staticmethod
    def _extract_class_hints(meaningful_tokens: List[str]) -> List[str]:
        """Map extracted meaningful tokens to OKS candidate class names."""
        hints: List[str] = []
        seen = set()
        for token in meaningful_tokens:
            t_lower = token.lower()
            if t_lower in _KEYWORD_TO_CLASS_HINTS:
                for cls in _KEYWORD_TO_CLASS_HINTS[t_lower]:
                    if cls not in seen:
                        hints.append(cls)
                        seen.add(cls)
        return hints

    @staticmethod
    def _extract_constraints(question: str) -> List[ConstraintHint]:
        """Detect comparison phrases (e.g. 'greater than 2', '> 5') and extract constraints."""
        constraints: List[ConstraintHint] = []
        q_lower = question.lower()

        # Sort comparator phrases by length descending to match longest phrase first
        sorted_phrases = sorted(_COMPARATOR_MAP.keys(), key=len, reverse=True)

        for phrase in sorted_phrases:
            if phrase not in q_lower:
                continue

            op = _COMPARATOR_MAP[phrase]
            pattern = re.escape(phrase) + r'\s*([\'"]?)([a-zA-Z0-9_\.\-]+)\1'
            m = re.search(pattern, q_lower)
            if m:
                val = m.group(2)
                raw = f"{phrase} {val}"

                # Try to extract the attribute token right before the comparator phrase
                before = q_lower[:m.start()].strip()
                words_before = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', before)
                attr_hint = None
                if words_before:
                    candidate_attr = words_before[-1]
                    if candidate_attr not in _STOP_WORDS:
                        attr_hint = candidate_attr

                constraints.append(ConstraintHint(
                    raw_text=raw,
                    operator=op,
                    value=val,
                    attribute_hint=attr_hint,
                ))

        return constraints

    @staticmethod
    def _extract_numerics(question: str) -> List[str]:
        """Extract numeric values from question."""
        return re.findall(r'\b\d+(?:\.\d+)?\b', question)
