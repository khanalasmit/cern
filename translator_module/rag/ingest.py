import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

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

    def ingest_xml(self, xml_path: str):
        """Parses the oks_schema_examples.xml and builds the chunks."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Simple extraction logic tailored to the example XML
        for example in root.findall('.//example'):
            for schema_file in example.findall('.//schema-file'):
                schema_xml_str = schema_file.text
                if not schema_xml_str:
                    continue
                try:
                    schema_tree = ET.fromstring(schema_xml_str.strip())
                    for cls in schema_tree.findall('.//class'):
                        class_name = cls.get('name')
                        desc = cls.get('description', '')
                        
                        # Build a textual representation
                        content = f"Class: {class_name}\nDescription: {desc}\n"
                        for attr in cls.findall('.//attribute'):
                            content += f"Attribute: {attr.get('name')} (type: {attr.get('type')})\n"
                        for rel in cls.findall('.//relationship'):
                            content += f"Relationship: {rel.get('name')} (target: {rel.get('class-type')})\n"
                            
                        chunk = SchemaChunk(
                            id=class_name,
                            content=content,
                            metadata={"type": "class", "name": class_name}
                        )
                        self.chunks.append(chunk)
                except ET.ParseError:
                    pass
        
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
