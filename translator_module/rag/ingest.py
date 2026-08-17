import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Set
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import networkx as nx

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
        self.graph = nx.DiGraph()

    def ingest_xml(self, xml_path: str):
        """Parses the oks_schema_examples.xml and builds the chunks with inheritance resolution."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        class_definitions = {}

        # Pass 1: Extract all raw class definitions
        for example in root.findall('.//example'):
            for schema_file in example.findall('.//schema-file'):
                schema_xml_str = schema_file.text
                if not schema_xml_str:
                    continue
                try:
                    schema_tree = ET.fromstring(schema_xml_str.strip())
                    for cls in schema_tree.findall('.//class'):
                        class_name = cls.get('name')
                        if class_name in class_definitions:
                            continue
                            
                        desc = cls.get('description', '')
                        superclasses = [sc.get('name') for sc in cls.findall('.//superclass')]
                        attributes = []
                        for a in cls.findall('.//attribute'):
                            attr_info = {
                                'name': a.get('name'),
                                'type': a.get('type'),
                                'range': a.get('range', ''),
                                'init_value': a.get('init-value', ''),
                                'is_multi_value': a.get('is-multi-value', 'no'),
                            }
                            attributes.append(attr_info)
                        relationships = [(r.get('name'), r.get('class-type')) for r in cls.findall('.//relationship')]
                        
                        class_definitions[class_name] = {
                            "name": class_name,
                            "description": desc,
                            "superclasses": superclasses,
                            "attributes": attributes,
                            "relationships": relationships
                        }
                except ET.ParseError:
                    pass

        # Helper to recursively get all superclasses
        def get_all_superclasses(cls_name: str, visited: Set[str]) -> List[str]:
            if cls_name not in class_definitions or cls_name in visited:
                return []
            visited.add(cls_name)
            parents = class_definitions[cls_name]["superclasses"]
            all_parents = list(parents)
            for parent in parents:
                all_parents.extend(get_all_superclasses(parent, visited))
            return all_parents

        # Pass 2: Resolve inheritance, build graph, and create chunks
        for class_name, def_dict in class_definitions.items():
            self.graph.add_node(class_name, **def_dict)
            
            all_superclasses = get_all_superclasses(class_name, set())
            
            # Combine attributes and relationships
            all_attrs = list(def_dict["attributes"])
            all_rels = list(def_dict["relationships"])
            
            for parent_name in all_superclasses:
                if parent_name in class_definitions:
                    parent_def = class_definitions[parent_name]
                    all_attrs.extend(parent_def["attributes"])
                    all_rels.extend(parent_def["relationships"])
                    self.graph.add_edge(class_name, parent_name, type="subclass_of")

            # Add relationship edges
            for rel_name, rel_target in all_rels:
                if rel_target:
                    self.graph.add_edge(class_name, rel_target, type="relationship", name=rel_name)

            # Build closed schema slice textual representation
            content = f"Class: {class_name}\nDescription: {def_dict['description']}\n"
            if all_superclasses:
                content += f"Inherits from: {', '.join(set(all_superclasses))}\n"
            for attr in all_attrs:
                attr_line = f"Attribute: {attr['name']} (type: {attr['type']}"
                if attr['range']:
                    attr_line += f", range: {attr['range']}"
                if attr['init_value']:
                    attr_line += f", init-value: {attr['init_value']}"
                if attr['is_multi_value'] == 'yes':
                    attr_line += ", multi-value: yes"
                attr_line += ")"
                content += attr_line + "\n"
            for rel_name, rel_target in all_rels:
                content += f"Relationship: {rel_name} (target: {rel_target})\n"
                
            chunk = SchemaChunk(
                id=class_name,
                content=content,
                metadata={"type": "class", "name": class_name}
            )
            self.chunks.append(chunk)

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
