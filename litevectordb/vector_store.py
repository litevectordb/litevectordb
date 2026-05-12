# litevectordb/vector_store.py
from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

import numpy as np

from litevectordb.index.linear import LinearIndex


def _matches_metadata(metadata: Dict[str, Any], where: Optional[Dict[str, Any]]) -> bool:
    if not where:
        return True

    for key, expected in where.items():
        actual = metadata.get(key)
        if isinstance(expected, (list, tuple, set)):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


class VectorStore:
    """
    Mini banco vetorial local baseado em SQLite + NumPy.
    Estilo Chroma, mas bem leve.
    """

    def __init__(self, path: str, dim: int):
        """
        path: caminho do arquivo .db (ex: "memories.db")
        dim: dimensão dos vetores (ex: 1536)
        """
        self.path = path
        self.dim = dim
        self._conn = sqlite3.connect(self.path)
        self._conn.execute("PRAGMA journal_mode=WAL;")  # melhor p/ concorrência leve
        self._create_schema()

        self.index = LinearIndex(dim=self.dim)
        self._load_index()

    def _load_index(self):
        """Carrega vetores do disco para a memória no startup"""
        cur = self._conn.cursor()
        cur.execute("SELECT id, vector FROM documents")
        rows = cur.fetchall()
        
        if not rows:
            return

        ids = []
        vectors = []
        for doc_id, blob in rows:
            ids.append(str(doc_id))
            vectors.append(self._decode_vector(blob))
        
        if ids:
            self.index.add(ids, np.array(vectors))

    # ---------- setup ----------

    def _create_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                content TEXT,
                metadata TEXT,
                vector BLOB NOT NULL,
                dim INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        self._conn.commit()

    # ---------- helpers de encode/decode ----------

    def _encode_vector(self, v: np.ndarray) -> bytes:
        v = np.asarray(v, dtype=np.float32)
        if v.shape != (self.dim,):
            raise ValueError(
                f"expected vector of shape ({self.dim},), got {v.shape}"
            )
        return v.tobytes()

    def _decode_vector(self, blob: bytes) -> np.ndarray:
        return np.frombuffer(blob, dtype=np.float32)

    # ---------- operações básicas ----------

    def add(
        self,
        vector: np.ndarray,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        key: Optional[str] = None,
    ) -> int:
        """
        Insere um novo documento vetorial.
        Retorna o id (int) gerado pelo banco.
        """
        blob = self._encode_vector(vector)
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)

        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO documents (key, content, metadata, vector, dim)
            VALUES (?, ?, ?, ?, ?)
            """,
            (key, content, meta_json, blob, self.dim),
        )
        self._conn.commit()
        
        doc_id = cur.lastrowid
        self.index.add([str(doc_id)], np.array([vector]))
        
        return doc_id

    def upsert(
        self,
        vector: np.ndarray,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        key: Optional[str] = None,
    ) -> int:
        """
        Insere ou atualiza por 'key'.
        Se key existir: atualiza content/metadata/vector.
        Se não existir: insere novo registro.
        """
        if key is None:
            # sem key, cai no add normal
            return self.add(vector, content, metadata, key=None)

        blob = self._encode_vector(vector)
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)

        cur = self._conn.cursor()
        cur.execute("SELECT id FROM documents WHERE key = ?", (key,))
        row = cur.fetchone()

        if row:
            doc_id = row[0]
            cur.execute(
                """
                UPDATE documents
                SET content = ?, metadata = ?, vector = ?, dim = ?
                WHERE id = ?
                """,
                (content, meta_json, blob, self.dim, doc_id),
            )
            self._conn.commit()
            
            # Atualiza índice
            self.index.add([str(doc_id)], np.array([vector]))
            
            return doc_id
        else:
            return self.add(vector, content, metadata, key=key)

    def get(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um documento por id.
        """
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT id, key, content, metadata, vector
            FROM documents WHERE id = ?
            """,
            (doc_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        _id, key, content, meta_json, blob = row
        return {
            "id": _id,
            "key": key,
            "content": content,
            "metadata": json.loads(meta_json or "{}"),
            "vector": self._decode_vector(blob),
        }

    def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT id, key, content, metadata, vector
            FROM documents WHERE key = ?
            """,
            (key,),
        )
        row = cur.fetchone()
        if not row:
            return None

        _id, key, content, meta_json, blob = row
        return {
            "id": _id,
            "key": key,
            "content": content,
            "metadata": json.loads(meta_json or "{}"),
            "vector": self._decode_vector(blob),
        }

    def list(
        self,
        where: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT id, key, content, metadata, vector
            FROM documents
            ORDER BY id
        """
        params = []
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cur = self._conn.cursor()
        cur.execute(query, params)

        records = []
        for _id, key, content, meta_json, blob in cur.fetchall():
            metadata = json.loads(meta_json or "{}")
            if _matches_metadata(metadata, where):
                records.append({
                    "id": _id,
                    "key": key,
                    "content": content,
                    "metadata": metadata,
                    "vector": self._decode_vector(blob),
                })
        return records

    def delete(self, doc_id: int) -> None:
        self.index.remove([str(doc_id)])
        cur = self._conn.cursor()
        cur.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self._conn.commit()

    def delete_by_key(self, key: str) -> None:
        cur = self._conn.cursor()
        # Precisa buscar ID antes de deletar p/ atualizar índice
        cur.execute("SELECT id FROM documents WHERE key = ?", (key,))
        row = cur.fetchone()
        if row:
            doc_id = row[0]
            self.index.remove([str(doc_id)])
            cur.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            self._conn.commit()

    def delete_where(self, where: Dict[str, Any]) -> int:
        records = self.list(where=where)
        if not records:
            return 0

        ids = [record["id"] for record in records]
        self.index.remove([str(doc_id) for doc_id in ids])
        placeholders = ",".join(["?"] * len(ids))

        cur = self._conn.cursor()
        cur.execute(f"DELETE FROM documents WHERE id IN ({placeholders})", ids)
        self._conn.commit()
        return int(cur.rowcount)

    def update_metadata(self, doc_id: int, metadata: Dict[str, Any]) -> bool:
        record = self.get(doc_id)
        if record is None:
            return False

        merged = {**record["metadata"], **metadata}
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE documents SET metadata = ? WHERE id = ?",
            (json.dumps(merged, ensure_ascii=False), doc_id),
        )
        self._conn.commit()
        return True

    # ---------- busca vetorial (cosine) ----------

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        min_score: float = -1.0,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca usando o índice vetorial interno.
        """
        candidates_k = self.count() if where else top_k
        results_index = self.index.search(query_vector, k=max(candidates_k, top_k))
        
        # Filtra por score min
        results_index = [r for r in results_index if r[1] >= min_score]
        
        if not results_index:
            return []

        # Recupera metadados do SQLite
        # ids no índice são strings, precisamos de ints
        ids_map = {int(r[0]): r[1] for r in results_index}
        ids_list = list(ids_map.keys())
        
        if not ids_list:
            return []

        placeholders = ",".join(["?"] * len(ids_list))
        cur = self._conn.cursor()
        query_sql = f"""
            SELECT id, key, content, metadata
            FROM documents 
            WHERE id IN ({placeholders})
        """
        cur.execute(query_sql, ids_list)
        rows = cur.fetchall()

        final_results = []
        for _id, key, content, meta_json in rows:
            metadata = json.loads(meta_json or "{}")
            if not _matches_metadata(metadata, where):
                continue

            score = ids_map.get(_id, 0.0)
            final_results.append({
                "id": _id,
                "key": key,
                "content": content,
                "metadata": metadata,
                "score": score,
            })

        # Reordena porque SQL IN não garante ordem
        final_results.sort(key=lambda r: r["score"], reverse=True)
        return final_results[:top_k]

    # ---------- utilidades ----------

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        if where:
            return len(self.list(where=where))

        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        return int(cur.fetchone()[0])

    def export_jsonl(
        self,
        path: str,
        where: Optional[Dict[str, Any]] = None,
    ) -> int:
        records = self.list(where=where)
        with open(path, "w", encoding="utf-8") as handle:
            for record in records:
                record = {**record, "vector": record["vector"].astype(float).tolist()}
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return len(records)

    def import_jsonl(self, path: str, replace: bool = False) -> int:
        inserted = 0
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue

                record = json.loads(line)
                vector = np.asarray(record["vector"], dtype=np.float32)
                method = self.upsert if replace else self.add
                method(
                    vector=vector,
                    content=record.get("content") or "",
                    metadata=record.get("metadata") or {},
                    key=record.get("key"),
                )
                inserted += 1
        return inserted

    def close(self) -> None:
        self._conn.close()
