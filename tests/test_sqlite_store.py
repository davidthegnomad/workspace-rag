import tempfile
import unittest
from pathlib import Path

from shared.store.sqlite_store import SqliteVectorStore


class SqliteStoreTest(unittest.TestCase):
    def test_keyword_hit_survives_when_the_vector_does_not_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteVectorStore(Path(tmp) / "index.sqlite")
            store.upsert_chunk({
                "source_path": "notes/budget.md",
                "chunk_index": 0,
                "content": "The board meets monthly about the grant.",
                "embedding": [1.0, 0.0],
                "domain": "notes",
                "project": "budget",
                "doc_type": "general",
                "title": "Budget",
            })
            store.upsert_chunk({
                "source_path": "notes/codes.md",
                "chunk_index": 0,
                "content": "The part number is ZX-4491.",
                "embedding": [0.0, 1.0],
                "domain": "notes",
                "project": "codes",
                "doc_type": "general",
                "title": "Codes",
            })
            results = store.search([1.0, 0.0], limit=5, threshold=0.8, query_text="ZX-4491")
            paths = [item.source_path for item in results]
            self.assertIn("notes/codes.md", paths)
            self.assertIn("notes/budget.md", paths)

    def test_reindex_replaces_the_old_chunk(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteVectorStore(Path(tmp) / "index.sqlite")
            record = {
                "source_path": "a.md",
                "chunk_index": 0,
                "content": "first",
                "embedding": [1.0, 0.0],
                "domain": "a",
                "project": "a",
                "doc_type": "general",
                "title": "A",
            }
            store.upsert_chunk(record)
            record["content"] = "second"
            store.upsert_chunk(record)
            self.assertEqual(store.count(), 1)
            hit = store.search([1.0, 0.0], limit=1, threshold=0.5, query_text="second")
            self.assertEqual(hit[0].content, "second")


if __name__ == "__main__":
    unittest.main()
