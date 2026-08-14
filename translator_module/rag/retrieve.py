from .ingest import HybridIndexer, SchemaChunk
from typing import List

class Retriever:
    def __init__(self, indexer: HybridIndexer):
        self.indexer = indexer

    def get_schema_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves top schema chunks for a query and formats them as a context string."""
        chunks: List[SchemaChunk] = self.indexer.retrieve(query, top_k=top_k)
        
        context_str = "--- Relevant OKS Schema Context ---\n"
        for chunk in chunks:
            context_str += f"{chunk.content}\n---\n"
            
        return context_str
