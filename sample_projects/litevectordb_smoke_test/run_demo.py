from __future__ import annotations

import tempfile
from pathlib import Path

from litevectordb import LocalVectorDB, MemoryDB, __version__


def main() -> None:
    workspace = Path(tempfile.mkdtemp(prefix="litevectordb-smoke-"))

    db = LocalVectorDB(path=str(workspace / "knowledge.db"), dim=48)
    db.add_texts(
        texts=[
            "FastAPI ajuda a criar APIs modernas em Python.",
            "SQLite armazena dados localmente em um unico arquivo.",
            "RAG local combina embeddings, busca semantica e contexto.",
        ],
        metadatas=[
            {"categoria": "web", "lang": "pt"},
            {"categoria": "database", "lang": "pt"},
            {"categoria": "ai", "lang": "pt"},
        ],
        keys=["fastapi", "sqlite", "rag-local"],
    )

    filtered = db.similarity_search("Como criar API em Python?", top_k=2, where={"categoria": "web"})
    assert len(filtered) == 1
    assert filtered[0].key == "fastapi"

    upsert_id = db.upsert_texts(
        ["FastAPI cria APIs HTTP modernas, rapidas e tipadas."],
        keys=["fastapi"],
        metadatas=[{"categoria": "web", "lang": "pt", "updated": True}],
    )[0]
    assert db.get(key="fastapi")["id"] == upsert_id
    assert db.get(key="fastapi")["metadata"]["updated"] is True

    memory = MemoryDB(db_path=str(workspace / "memory.db"), dim=48)
    memory.remember("demo-session", "O usuario esta avaliando LiteVectorDB para RAG local.")
    memory.remember("other-session", "Outro usuario esta estudando bancos relacionais.")
    recalled = memory.recall("demo-session", "RAG local", top_k=3, min_score=-1.0)
    assert len(recalled) == 1
    assert recalled[0]["metadata"]["session_id"] == "demo-session"

    print(f"LiteVectorDB {__version__} smoke test passed")
    print(f"Search result: {filtered[0].key} score={filtered[0].score:.4f}")
    print(f"Memory result: {recalled[0]['content']}")


if __name__ == "__main__":
    main()
