import os
import math
import re
from typing import List, Dict, Any, Optional
from app.config import settings

class VectorDatabaseService:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.collection_name = "security_presales_docs"
        self._client = None
        self._collection = None
        self._embedder = None
        self._fallback_corpus: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            os.makedirs(self.persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Security Presales Solutions & Knowledge Base"}
            )
            print("Successfully initialized ChromaDB collection.")
        except Exception as e:
            print(f"Warning: ChromaDB initialization error ({e}). Using in-memory fallback store.")
            self._client = None
            self._collection = None

    def _get_embedding(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds texts using sentence-transformers or OpenAI or a lightweight fallback embedding.
        """
        try:
            if settings.EMBEDDING_PROVIDER == "sentence-transformers":
                if self._embedder is None:
                    from sentence_transformers import SentenceTransformer
                    self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                embeddings = self._embedder.encode(texts, convert_to_numpy=True).tolist()
                return embeddings
        except Exception as e:
            print(f"Embedding model load notice ({e}). Using normalized term vector fallback.")
        
        # Fast fallback deterministic embedding vector (size 128)
        embeddings = []
        for text in texts:
            vec = [0.0] * 128
            words = re.findall(r'\w+', text.lower())
            for i, word in enumerate(words):
                h = hash(word) % 128
                vec[h] += 1.0 / (1.0 + math.log(i + 1))
            # Normalize vector
            norm = math.sqrt(sum(x*x for x in vec)) or 1.0
            embeddings.append([x / norm for x in vec])
        return embeddings

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Adds parsed document chunks into the vector store.
        """
        if not chunks:
            return 0

        ids = [chunk["chunk_id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # In-memory fallback tracking
        for chunk in chunks:
            self._fallback_corpus.append(chunk)

        if self._collection is not None:
            try:
                embeddings = self._get_embedding(texts)
                # ChromaDB upsert chunks
                self._collection.upsert(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
                return len(chunks)
            except Exception as e:
                print(f"Error upserting into ChromaDB: {e}")
                
        return len(chunks)

    def query_similar(self, query: str, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search against knowledge base.
        """
        if self._collection is not None:
            try:
                query_embedding = self._get_embedding([query])[0]
                where_clause = filter_dict if filter_dict else None
                
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k, max(1, self._collection.count())),
                    where=where_clause
                )
                
                output = []
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                    ids = results["ids"][0] if "ids" in results else [""] * len(docs)
                    distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
                    
                    for i in range(len(docs)):
                        output.append({
                            "chunk_id": ids[i],
                            "text": docs[i],
                            "metadata": metas[i],
                            "distance": distances[i] if i < len(distances) else 0.0
                        })
                if output:
                    return output
            except Exception as e:
                print(f"ChromaDB query error: {e}. Falling back to keyword search.")

        # Fallback keyword & semantic ranker
        return self._keyword_search_fallback(query, top_k)

    def _keyword_search_fallback(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        query_terms = set(re.findall(r'\w+', query.lower()))
        scored = []
        for item in self._fallback_corpus:
            text = item["text"]
            score = 0
            for term in query_terms:
                if len(term) > 2 and term in text.lower():
                    score += text.lower().count(term)
            if score > 0:
                scored.append((score, item))
                
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"chunk_id": it[1]["chunk_id"], "text": it[1]["text"], "metadata": it[1]["metadata"], "distance": 0.5} for it in scored[:top_k]]

    def get_collection_count(self) -> int:
        if self._collection is not None:
            try:
                return self._collection.count()
            except Exception:
                pass
        return len(self._fallback_corpus)

vector_service = VectorDatabaseService()
