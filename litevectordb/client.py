# litevectordb/client.py
from __future__ import annotations
from typing import Callable, Iterable, List, Dict, Any, Optional
import numpy as np

from .vector_store import VectorStore
from .embeddings import fake_embed  # depois você troca pelo real

EmbeddingFn = Callable[[str, int], Iterable[float]]


class DocumentResult:
    def __init__(self, id: int, text: str, metadata: dict, score: float, key: Optional[str] = None):
        self.id = id
        self.key = key
        self.text = text
        self.metadata = metadata
        self.score = score


class LocalVectorDB:
    """
    Interface simples p/ usar direto, sem collections.
    """

    def __init__(
        self,
        path: str = "litevectordb.db",
        dim: int = 64,
        embedding_fn: Optional[EmbeddingFn] = None,
    ):
        self._store = VectorStore(path, dim=dim)
        self.dim = dim
        self.embedding_fn = embedding_fn or fake_embed

    def embed(self, text: str) -> np.ndarray:
        return np.asarray(list(self.embedding_fn(text, self.dim)), dtype=np.float32)

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        keys: Optional[List[str]] = None,
    ) -> List[int]:
        metadatas = metadatas or [{} for _ in texts]
        keys = keys or ids
        if ids and len(ids) != len(texts):
            raise ValueError("len(ids) != len(texts)")
        if keys and len(keys) != len(texts):
            raise ValueError("len(keys) != len(texts)")

        inserted_ids: List[int] = []
        for i, text in enumerate(texts):
            vec = self.embed(text)
            key = keys[i] if keys else None
            doc_id = self._store.add(
                vector=vec,
                content=text,
                metadata=metadatas[i],
                key=key,
            )
            inserted_ids.append(doc_id)
        return inserted_ids

    def upsert_texts(
        self,
        texts: List[str],
        keys: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[int]:
        metadatas = metadatas or [{} for _ in texts]
        if len(keys) != len(texts):
            raise ValueError("len(keys) != len(texts)")
        if len(metadatas) != len(texts):
            raise ValueError("len(metadatas) != len(texts)")

        return [
            self._store.upsert(
                vector=self.embed(text),
                content=text,
                metadata=metadata,
                key=key,
            )
            for text, key, metadata in zip(texts, keys, metadatas)
        ]

    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.2,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentResult]:
        q_vec = self.embed(query)
        raw_results = self._store.search(
            query_vector=q_vec,
            top_k=top_k,
            min_score=min_score,
            where=where,
        )
        return [
            DocumentResult(
                id=r["id"],
                key=r["key"],
                text=r["content"],
                metadata=r["metadata"],
                score=r["score"],
            )
            for r in raw_results
        ]

    def get(self, id: Optional[int] = None, key: Optional[str] = None):
        if id is None and key is None:
            raise ValueError("id or key is required")
        return self._store.get(id) if id is not None else self._store.get_by_key(key)

    def delete(
        self,
        id: Optional[int] = None,
        key: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> int:
        if id is not None:
            self._store.delete(id)
            return 1
        if key is not None:
            self._store.delete_by_key(key)
            return 1
        if where:
            return self._store.delete_where(where)
        raise ValueError("id, key or where is required")

    def update_metadata(
        self,
        id: Optional[int] = None,
        key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        record = self.get(id=id, key=key)
        if record is None:
            return False
        return self._store.update_metadata(record["id"], metadata or {})

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        return self._store.count(where=where)

    def export_jsonl(self, path: str, where: Optional[Dict[str, Any]] = None) -> int:
        return self._store.export_jsonl(path, where=where)

    def import_jsonl(self, path: str, replace: bool = False) -> int:
        return self._store.import_jsonl(path, replace=replace)

    def close(self) -> None:
        self._store.close()
