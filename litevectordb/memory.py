# litevectordb/memory.py
from __future__ import annotations

from datetime import datetime
import numpy as np

from .vector_store import VectorStore
from .embeddings import fake_embed  # troque depois por openai/ollama


class MemoryDB:
    """
    Camada de alto nível: memória estilo Chroma.
    Usa o VectorStore por baixo.
    """

    def __init__(self, db_path: str, dim: int = 64):
        self.store = VectorStore(db_path, dim=dim)
        self.dim = dim

    # ============================================================
    # Gravar memória
    # ============================================================
    def store_memory(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict = None,
    ) -> int:
        """
        Gera embedding do conteúdo e salva como memória.
        """
        vec = fake_embed(content, dim=self.dim)

        key = f"{session_id}:{datetime.utcnow().isoformat()}"
        metadata = metadata or {}
        metadata.update({"session_id": session_id, "role": role})

        return self.store.add(
            vector=vec,
            content=content,
            metadata=metadata,
            key=key,
        )

    def remember(
        self,
        session_id: str,
        content: str,
        metadata: dict = None,
        role: str = "user",
    ) -> int:
        return self.store_memory(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata,
        )

    # ============================================================
    # Recuperar memórias relevantes
    # ============================================================
    def retrieve_memory(
        self,
        session_id: str,
        query: str,
        top_k: int = 5,
        min_score: float = 0.2,
    ):
        """
        Busca vetorial + filtro por sessão.
        """
        q_vec = fake_embed(query, dim=self.dim)
        return self.store.search(
            q_vec,
            top_k=top_k,
            min_score=min_score,
            where={"session_id": session_id},
        )

    def recall(
        self,
        session_id: str,
        query: str,
        top_k: int = 5,
        min_score: float = 0.2,
    ):
        return self.retrieve_memory(
            session_id=session_id,
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

    def forget(self, session_id: str) -> int:
        return self.store.delete_where({"session_id": session_id})

    # ============================================================
    # Utilidades
    # ============================================================
    def count(self, session_id: str = None):
        return self.store.count({"session_id": session_id} if session_id else None)

    def close(self):
        self.store.close()
