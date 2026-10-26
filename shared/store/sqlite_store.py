"""Local index. Vectors for meaning, SQLite FTS5 (BM25) for exact words."""

from __future__ import annotations

import json
import math
import re
import sqlite3
from pathlib import Path
from typing import Any

from shared.store.results import SearchResult

RRF_K = 60


def cosine(a: list[float], b: list[float]) -> float:
    dot = norm_a = norm_b = 0.0
    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / math.sqrt(norm_a * norm_b)


def fts_query(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9']{2,}", text or "")
    if not words:
        return ""
    return " OR ".join(f'"{word}"' for word in words[:12])


class SqliteVectorStore:
    """One SQLite file. No account and no server."""

    def __init__(self, db_path: Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                source_path TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT NOT NULL,
                domain TEXT,
                project TEXT,
                doc_type TEXT,
                title TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_path);
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                id UNINDEXED,
                content,
                source_path,
                title
            );
            """
        )
        self.conn.commit()

    def upsert_chunk(self, record: dict[str, Any]) -> None:
        source_path = record["source_path"]
        chunk_index = int(record["chunk_index"])
        doc_id = f"{source_path}#{chunk_index}"
        self.conn.execute("DELETE FROM chunks_fts WHERE id = ?", (doc_id,))
        self.conn.execute(
            """
            INSERT INTO chunks (id, source_path, chunk_index, content, embedding, domain, project, doc_type, title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                content=excluded.content,
                embedding=excluded.embedding,
                domain=excluded.domain,
                project=excluded.project,
                doc_type=excluded.doc_type,
                title=excluded.title
            """,
            (
                doc_id,
                source_path,
                chunk_index,
                record.get("content", ""),
                json.dumps(record.get("embedding") or []),
                record.get("domain", ""),
                record.get("project", ""),
                record.get("doc_type", ""),
                record.get("title", ""),
            ),
        )
        self.conn.execute(
            "INSERT INTO chunks_fts (id, content, source_path, title) VALUES (?, ?, ?, ?)",
            (doc_id, record.get("content", ""), source_path, record.get("title", "")),
        )
        self.conn.commit()

    def delete_by_source_path(self, source_path: str) -> int:
        ids = [
            row["id"]
            for row in self.conn.execute("SELECT id FROM chunks WHERE source_path = ?", (source_path,))
        ]
        if not ids:
            return 0
        self.conn.executemany("DELETE FROM chunks WHERE id = ?", [(item,) for item in ids])
        self.conn.executemany("DELETE FROM chunks_fts WHERE id = ?", [(item,) for item in ids])
        self.conn.commit()
        return len(ids)

    def count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
        return int(row["n"])

    def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        threshold: float = 0.7,
        filters: dict[str, str] | None = None,
        query_text: str = "",
    ) -> list[SearchResult]:
        rows = self.conn.execute(
            "SELECT id, source_path, content, embedding, domain, project, doc_type, title FROM chunks"
        ).fetchall()
        if filters:
            rows = [row for row in rows if all(row[key] == value for key, value in filters.items())]

        scored = []
        for row in rows:
            try:
                vector = json.loads(row["embedding"])
            except json.JSONDecodeError:
                continue
            score = cosine(query_embedding, vector)
            if score >= threshold:
                scored.append((score, row))
        scored.sort(key=lambda item: item[0], reverse=True)
        vector_hits = scored[: max(limit * 3, limit)]

        fts_hits = []
        match = fts_query(query_text)
        if match:
            try:
                fts_hits = self.conn.execute(
                    """
                    SELECT id FROM chunks_fts
                    WHERE chunks_fts MATCH ?
                    ORDER BY bm25(chunks_fts)
                    LIMIT ?
                    """,
                    (match, max(limit * 3, limit)),
                ).fetchall()
            except sqlite3.OperationalError:
                fts_hits = []

        by_id = {row["id"]: (score, row) for score, row in vector_hits}
        ranks: dict[str, float] = {}
        for rank, (score, row) in enumerate(vector_hits):
            ranks[row["id"]] = ranks.get(row["id"], 0.0) + 1.0 / (RRF_K + rank + 1)
        for rank, hit in enumerate(fts_hits):
            ranks[hit["id"]] = ranks.get(hit["id"], 0.0) + 1.0 / (RRF_K + rank + 1)

        ordered = sorted(ranks, key=lambda item: ranks[item], reverse=True)[:limit]
        results = []
        for doc_id in ordered:
            if doc_id in by_id:
                score, row = by_id[doc_id]
            else:
                row = self.conn.execute("SELECT * FROM chunks WHERE id = ?", (doc_id,)).fetchone()
                if row is None:
                    continue
                score = 0.0
            results.append(
                SearchResult(
                    content=row["content"],
                    source_path=row["source_path"],
                    domain=row["domain"] or "",
                    project=row["project"] or "",
                    doc_type=row["doc_type"] or "",
                    similarity=score,
                    title=row["title"] or "",
                )
            )
        return results
