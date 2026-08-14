import json
import random
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer


class FewShotManager:
    def __init__(self, jsonl_path: str, encoder: Optional[SentenceTransformer] = None):
        self.examples = []
        self.encoder = encoder
        self.embeddings = None

        try:
            with open(jsonl_path, 'r') as f:
                for line in f:
                    if line.strip():
                        self.examples.append(json.loads(line))
        except FileNotFoundError:
            pass

        # Pre-compute embeddings for semantic retrieval
        if self.examples and self.encoder is not None:
            try:
                questions = [ex.get('question', '') for ex in self.examples]
                self.embeddings = self.encoder.encode(questions, normalize_embeddings=True)
            except Exception:
                self.embeddings = None

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
