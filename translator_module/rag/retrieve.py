from .ingest import HybridIndexer, SchemaChunk
from typing import List
from sentence_transformers import CrossEncoder
import numpy as np

class Retriever:
    def __init__(self, indexer: HybridIndexer):
        self.indexer = indexer
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def get_schema_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves top schema chunks for a query, reranks them, and formats as a context string."""
        # 1. Retrieve wider candidate set (e.g. 20)
        candidate_chunks: List[SchemaChunk] = self.indexer.retrieve(query, top_k=20)
        
        if not candidate_chunks:
            return "--- Relevant OKS Schema Context ---\nNo relevant context found.\n---\n"

        # 2. Rerank candidates
        cross_inp = [[query, chunk.content] for chunk in candidate_chunks]
        scores = self.reranker.predict(cross_inp)
        
        # 3. Sort by scores and get top_k
        top_indices = np.argsort(scores)[::-1][:top_k]
        top_chunks = [candidate_chunks[i] for i in top_indices]
        
        # 4. Format context
        context_str = "--- Relevant OKS Schema Context ---\n"
        for chunk in top_chunks:
            context_str += f"{chunk.content}\n---\n"
            
        return context_str
