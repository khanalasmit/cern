"""
few_shot.py — Dynamic Few-Shot Example Discovery & Selection
=============================================================

Discovers and loads NL→OksQuery example pairs from the repository at
runtime.  Selects the most relevant examples for a given user question
using BM25 keyword matching, with fallbacks to random sampling and
built-in canonical examples.

Data sources (tried in priority order):
  1. combined_data/all_few_shot.jsonl  (184 examples)
  2. oks_scraped/gold_pairs_clean.jsonl (40 curated examples)
  3. Built-in fallback (6 canonical examples from breif.md Section 9)
"""

import json
import os
import random
from typing import Dict, List, Optional

# rank_bm25 is a lightweight pure-Python BM25 implementation
try:
    from rank_bm25 import BM25Okapi
    _HAS_BM25 = True
except ImportError:
    _HAS_BM25 = False


# ---------------------------------------------------------------------------
# Built-in fallback examples (breif.md Section 9)
# Used only when no JSONL files are found in the repo.
# ---------------------------------------------------------------------------
_BUILTIN_EXAMPLES = [
    {
        "question": "Which test executables take longer than 2 seconds to initialise?",
        "target_class": "Executable",
        "query_oks": '(all ("InitTimeout" "2" >))',
        "note": "'>' on numeric attribute. Value is quoted despite being numeric."
    },
    {
        "question": "Which test executables run on the object's own host?",
        "target_class": "Executable",
        "query_oks": '(all ("Host" "#this.UID" =))',
        "note": "#this.UID is a DAL substitution token stored verbatim."
    },
    {
        "question": "Which applications initialise in 30 seconds and exit within 5?",
        "target_class": "BaseApplication",
        "query_oks": '(all (and ("InitTimeout" "30" =) ("ExitTimeout" "5" =)))',
        "note": "'and' needs >=2 operands; scope token appears once at top."
    },
    {
        "question": "Which applications run on host lxplus001.cern.ch?",
        "target_class": "Application",
        "query_oks": '(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))',
        "note": "Relationship traversal with object-id comparison."
    },
    {
        "question": "Which applications have a name containing 'lxplus'?",
        "target_class": "Application",
        "query_oks": '(all ("Name" ".*lxplus.*" ~=))',
        "note": "'~=' is regex match. Pattern must match the whole value."
    },
    {
        "question": "List all Computer objects.",
        "target_class": "Computer",
        "query_oks": '(all (object-id "" !=))',
        "note": "Match-all pattern using object-id != empty string."
    },
]


class FewShotManager:
    """
    Manages few-shot example loading and retrieval.

    On init, discovers and loads examples from JSONL files in the repo.
    For each query, selects the most relevant examples using BM25 or
    random sampling.
    """

    def __init__(self, repo_root: str = None):
        """
        Parameters
        ----------
        repo_root : str, optional
            Path to the repository root.  Used to discover JSONL files.
            Defaults to two levels up from this file.
        """
        if repo_root is None:
            repo_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..")
            )
        self.repo_root = repo_root
        self.examples: List[Dict] = []
        self._bm25: Optional[object] = None
        self._tokenized_questions: Optional[List[List[str]]] = None

        self._discover_and_load()
        self._build_index()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_examples(self, question: str, top_k: int = 5) -> str:
        """
        Return a formatted string of the most relevant few-shot examples
        for the given question, ready for prompt injection.
        """
        selected = self._select(question, top_k)
        if not selected:
            return "--- Few-Shot Examples ---\nNo examples available.\n"

        lines = ["--- Few-Shot Examples ---"]
        for ex in selected:
            q = ex.get("question", "")
            cls = ex.get("target_class", "")
            a = ex.get("query_oks", "")
            note = ex.get("note", "")
            lines.append(f"Q: {q}")
            if cls:
                lines.append(f"Class: {cls}")
            lines.append(f"A: {a}")
            if note:
                lines.append(f"Note: {note}")
            lines.append("")
        return "\n".join(lines)

    def get_example_count(self) -> int:
        """Number of loaded examples."""
        return len(self.examples)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def _discover_and_load(self):
        """Search the repo for JSONL files and load examples."""
        candidate_paths = [
            "combined_data/all_few_shot.jsonl",
            "oks_scraped/gold_pairs_clean.jsonl",
            "oks_scraped/gold_pairs.jsonl",
        ]

        loaded_files = []
        seen_questions = set()  # deduplicate by question text

        for rel_path in candidate_paths:
            abs_path = os.path.join(self.repo_root, rel_path)
            if not os.path.isfile(abs_path):
                continue
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        # Normalize: ensure we have question and query_oks
                        question = record.get("question", "")
                        query = record.get("query_oks", "")
                        if not question or not query:
                            continue

                        # Deduplicate
                        if question in seen_questions:
                            continue
                        seen_questions.add(question)

                        self.examples.append({
                            "question": question,
                            "target_class": record.get("target_class", ""),
                            "query_oks": query,
                            "note": record.get("note", ""),
                            "difficulty": record.get("difficulty", ""),
                            "source_file": record.get("source_file", ""),
                        })
                loaded_files.append(rel_path)
            except Exception:
                continue

        # Fallback to built-in examples if nothing was found
        if not self.examples:
            self.examples = list(_BUILTIN_EXAMPLES)
            loaded_files = ["(built-in)"]

        self._loaded_from = loaded_files

    # ------------------------------------------------------------------
    # BM25 index
    # ------------------------------------------------------------------

    def _build_index(self):
        """Build BM25 index over the loaded example questions."""
        if not _HAS_BM25 or not self.examples:
            return
        self._tokenized_questions = [
            ex["question"].lower().split() for ex in self.examples
        ]
        try:
            self._bm25 = BM25Okapi(self._tokenized_questions)
        except Exception:
            self._bm25 = None

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def _select(self, question: str, top_k: int) -> List[Dict]:
        """Select the top-k most relevant examples for the question."""
        if not self.examples:
            return []

        top_k = min(top_k, len(self.examples))

        # Strategy 1: BM25 keyword matching
        if self._bm25 is not None:
            try:
                tokenized_query = question.lower().split()
                scores = self._bm25.get_scores(tokenized_query)
                # Get top-k indices
                top_indices = sorted(
                    range(len(scores)),
                    key=lambda i: scores[i],
                    reverse=True
                )[:top_k]
                return [self.examples[i] for i in top_indices]
            except Exception:
                pass

        # Strategy 2: Random stratified sampling
        # If difficulty labels exist, try to include a mix
        difficulties = {ex.get("difficulty", "") for ex in self.examples}
        if len(difficulties) > 1 and "" not in difficulties:
            stratified = []
            per_bucket = max(1, top_k // len(difficulties))
            for diff in sorted(difficulties):
                pool = [ex for ex in self.examples if ex.get("difficulty") == diff]
                stratified.extend(random.sample(pool, min(per_bucket, len(pool))))
            return stratified[:top_k]

        # Strategy 3: Plain random
        return random.sample(self.examples, top_k)
