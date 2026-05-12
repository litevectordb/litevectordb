from litevectordb import LocalVectorDB, MemoryDB


def test_similarity_search_with_metadata_filter(tmp_path):
    db = LocalVectorDB(path=str(tmp_path / "store.db"), dim=32)
    db.add_texts(
        ["FastAPI cria APIs em Python", "SQLite grava dados locais"],
        metadatas=[{"categoria": "web"}, {"categoria": "db"}],
    )

    results = db.similarity_search("API Python", top_k=5, min_score=-1.0, where={"categoria": "web"})

    assert len(results) == 1
    assert results[0].metadata["categoria"] == "web"


def test_upsert_keeps_key_and_replaces_content(tmp_path):
    db = LocalVectorDB(path=str(tmp_path / "store.db"), dim=32)

    first_id = db.upsert_texts(["texto antigo"], keys=["doc-1"])[0]
    second_id = db.upsert_texts(["texto novo"], keys=["doc-1"], metadatas=[{"v": 2}])[0]

    record = db.get(key="doc-1")
    assert first_id == second_id
    assert record is not None
    assert record["content"] == "texto novo"
    assert record["metadata"] == {"v": 2}


def test_export_import_jsonl(tmp_path):
    db = LocalVectorDB(path=str(tmp_path / "store.db"), dim=16)
    db.add_texts(["um", "dois"], keys=["a", "b"])
    export_path = tmp_path / "backup.jsonl"

    assert db.export_jsonl(str(export_path)) == 2

    restored = LocalVectorDB(path=str(tmp_path / "restored.db"), dim=16)
    assert restored.import_jsonl(str(export_path)) == 2
    assert restored.count() == 2


def test_memory_is_scoped_by_session(tmp_path):
    memory = MemoryDB(db_path=str(tmp_path / "memory.db"), dim=32)
    memory.remember("s1", "usuario gosta de Python")
    memory.remember("s2", "usuario gosta de Java")

    results = memory.recall("s1", "Python", top_k=5, min_score=-1.0)

    assert len(results) == 1
    assert results[0]["metadata"]["session_id"] == "s1"
