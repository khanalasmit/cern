import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterable, List, Optional
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

from translator_module.revision.source import FileSource, WorkingTreeSource
from .schema_loader import SchemaDocument, SchemaLoader

class SchemaChunk:
    def __init__(self, id: str, content: str, metadata: Dict[str, Any]):
        self.id = id
        self.content = content
        self.metadata = metadata

class HybridIndexer:
    def __init__(self):
        self.chunks: List[SchemaChunk] = []
        self.bm25: BM25Okapi = None
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.faiss_index = None
        self.revision: Optional[str] = None

    def ingest_xml(self, xml_path: str):
        """Parse a wrapper or standalone XML file from the working tree."""
        documents = SchemaLoader.load_file(xml_path)
        self._ingest_documents(documents)

    def ingest_source(
        self,
        source: FileSource,
        paths: Iterable[str],
        revision: Optional[str] = None,
    ):
        """Parse schema files supplied by a working-tree or Git source."""
        documents = SchemaLoader.load_source(source, paths)
        self.revision = revision
        self._ingest_documents(documents)

    def _ingest_documents(self, documents: Iterable[SchemaDocument]):
        self.chunks = []
        for document in documents:
            for cls in document.root.findall('.//class'):
                class_name = cls.get('name')
                if not class_name:
                    continue
                desc = cls.get('description', '')

                content = f"Class: {class_name}\nDescription: {desc}\n"
                for attr in cls.findall('.//attribute'):
                    content += (
                        f"Attribute: {attr.get('name')} "
                        f"(type: {attr.get('type')})\n"
                    )
                for rel in cls.findall('.//relationship'):
                    content += (
                        f"Relationship: {rel.get('name')} "
                        f"(target: {rel.get('class-type')})\n"
                    )

                metadata: Dict[str, Any] = {
                    "type": "class",
                    "name": class_name,
                    "source_path": document.source_path,
                }
                if self.revision:
                    metadata["revision"] = self.revision

                self.chunks.append(
                    SchemaChunk(
                        id=class_name,
                        content=content,
                        metadata=metadata,
                    )
                )

        self._build_indices()

    def _build_indices(self):
        if not self.chunks:
            return
            
        # Build BM25
        tokenized_corpus = [chunk.content.lower().split(" ") for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        # Build FAISS Vector Index
        embeddings = self.encoder.encode([chunk.content for chunk in self.chunks])
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(embeddings)

    def retrieve(self, query: str, top_k: int = 3) -> List[SchemaChunk]:
        if not self.chunks:
            return []
            
        # BM25 Search
        tokenized_query = query.lower().split(" ")
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:top_k]
        
        # Vector Search
        query_emb = self.encoder.encode([query])
        D, I = self.faiss_index.search(query_emb, top_k)
        vector_top_indices = I[0]
        
        # Simple Reciprocal Rank Fusion (RRF)
        rrf_scores = {i: 0.0 for i in range(len(self.chunks))}
        for rank, idx in enumerate(bm25_top_indices):
            rrf_scores[idx] += 1.0 / (60 + rank)
        for rank, idx in enumerate(vector_top_indices):
            if idx != -1: # faiss returns -1 if not enough results
                rrf_scores[idx] += 1.0 / (60 + rank)
                
        sorted_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)
        return [self.chunks[i] for i in sorted_indices[:top_k]]
