import json
import random
import numpy as np
from typing import Any, List, Dict, Optional

try:
    from sentence_transformers import SentenceTransformer
except ModuleNotFoundError:  # pragma: no cover - exercised by minimal test envs
    SentenceTransformer = Any

from translator_module.revision.source import FileSource


class FewShotManager:
    def __init__(
        self,
        jsonl_path: Optional[str],
        encoder: Optional[SentenceTransformer] = None,
        *,
        source: Optional[FileSource] = None,
        source_path: Optional[str] = None,
    ):
        self.examples = []
        self.encoder = encoder
        self.embeddings = None

        if source is not None:
            if not source_path:
                raise ValueError("source_path is required when source is supplied")
            try:
                payload = source.read_bytes(source_path).decode("utf-8")
            except (FileNotFoundError, OSError):
                payload = ""
            self._load_jsonl(payload)
        elif jsonl_path:
            try:
                with open(jsonl_path, 'r', encoding='utf-8') as f:
                    self._load_jsonl(f.read())
            except FileNotFoundError:
                pass

        # Pre-compute embeddings for semantic retrieval
        if self.examples and self.encoder is not None:
            try:
                questions = [ex.get('question', '') for ex in self.examples]
                self.embeddings = self.encoder.encode(questions, normalize_embeddings=True)
            except Exception:
                self.embeddings = None

    @classmethod
    def from_source(
        cls,
        source: FileSource,
        source_path: str,
        encoder: Optional[SentenceTransformer] = None,
    ):
        """Load examples from the same revision-backed source as the schema."""

        if not source.exists(source_path):
            # Match the legacy loader's missing-file behavior, but do not
            # fall back to a current working-tree file.
            return cls(None, encoder=encoder)

        return cls(
            None,
            encoder=encoder,
            source=source,
            source_path=source_path,
        )

    def _load_jsonl(self, payload: str):
        for line in payload.splitlines():
            if line.strip():
                self.examples.append(json.loads(line))

    def get_examples(self, query: str, top_k: int = 3) -> str:
        """Returns a formatted string of the most relevant few-shot examples."""
        if not self.examples:
            return "No examples available."

        selected = self._select_examples(query, top_k)

        examples_str = "--- Few-Shot Examples ---\n"
        for ex in selected:
            if "query_oks" in ex:
                examples_str += f"Q: {ex['question']}\nA: {ex['query_oks']}\nNote: {ex.get('note', '')}\n\n"

        return examples_str

    def _select_examples(self, query: str, top_k: int) -> List[Dict]:
        """Select examples by semantic similarity, falling back to random sampling."""
        if self.encoder is not None and self.embeddings is not None:
            try:
                query_emb = self.encoder.encode([query], normalize_embeddings=True)
                # Cosine similarity (embeddings are already normalized)
                similarities = np.dot(self.embeddings, query_emb.T).flatten()
                top_indices = np.argsort(similarities)[::-1][:top_k]
                return [self.examples[i] for i in top_indices]
            except Exception:
                pass

        # Fallback: random sampling
        return random.sample(self.examples, min(top_k, len(self.examples)))
