"""
Firestore vector store for RAG chunks.

Uses Firestore native vector search (find_nearest). Requires a vector index
on the `embedding` field — see internal/firebase/setup-index.sh.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector

from shared.store.results import SearchResult


def _chunk_doc_id(source_path: str, chunk_index: int) -> str:
    path_hash = hashlib.sha256(source_path.encode()).hexdigest()[:16]
    return f"{path_hash}_{chunk_index}"


class FirestoreVectorStore:
    """Vector store backed by Firestore with native KNN search."""

    def __init__(
        self,
        collection: str = "workspace_rag_chunks",
        project_id: str | None = None,
    ):
        self.collection_name = collection
        self._db = self._init_firestore(project_id)

    @staticmethod
    def _init_firestore(project_id: str | None):
        if not firebase_admin._apps:
            cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            pid = project_id or os.environ.get("FIREBASE_PROJECT_ID")
            if cred_path and os.path.isfile(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {"projectId": pid} if pid else None)
            elif pid:
                firebase_admin.initialize_app(options={"projectId": pid})
            else:
                firebase_admin.initialize_app()
        return firestore.client()

    @property
    def collection(self):
        return self._db.collection(self.collection_name)

    def upsert_chunk(self, record: dict[str, Any]) -> None:
        source_path = record["source_path"]
        chunk_index = record["chunk_index"]
        doc_id = _chunk_doc_id(source_path, chunk_index)
        payload = {
            **record,
            "embedding": Vector(record["embedding"]),
        }
        self.collection.document(doc_id).set(payload, merge=True)

    def delete_by_source_path(self, source_path: str) -> int:
        deleted = 0
        while True:
            docs = list(
                self.collection.where("source_path", "==", source_path).limit(400).stream()
            )
            if not docs:
                break
            batch = self._db.batch()
            for doc in docs:
                batch.delete(doc.reference)
                deleted += 1
            batch.commit()
        return deleted

    def clear_all(self) -> int:
        deleted = 0
        while True:
            docs = list(self.collection.limit(400).stream())
            if not docs:
                break
            batch = self._db.batch()
            for doc in docs:
                batch.delete(doc.reference)
                deleted += 1
            batch.commit()
        return deleted

    def count(self) -> int:
        agg = self.collection.count()
        result = agg.get()
        return int(result[0][0].value)

    def domain_stats(self) -> list[dict[str, str | int]]:
        """Aggregate chunk counts by domain (suitable for internal corpus sizes)."""
        counts: dict[str, int] = {}
        for doc in self.collection.select(["domain"]).stream():
            domain = doc.to_dict().get("domain") or "unknown"
            counts[domain] = counts.get(domain, 0) + 1
        return [{"domain": k, "count": v} for k, v in sorted(counts.items())]

    def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        threshold: float = 0.7,
        filters: dict[str, str] | None = None,
        query_text: str = "",
    ) -> list[SearchResult]:
        """
        Semantic search using Firestore find_nearest (COSINE).

        threshold is similarity (0–1); converted to Firestore distance threshold.
        """
        query = self.collection
        if filters:
            for field, value in filters.items():
                query = query.where(field, "==", value)

        distance_threshold = max(0.0, 1.0 - threshold)
        vector_query = query.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=limit,
            distance_result_field="vector_distance",
            distance_threshold=distance_threshold,
        )

        results = []
        for doc in vector_query.stream():
            data = doc.to_dict()
            distance = data.get("vector_distance", 1.0)
            similarity = max(0.0, 1.0 - distance)
            results.append(
                SearchResult(
                    content=data.get("content", ""),
                    source_path=data.get("source_path", ""),
                    domain=data.get("domain", ""),
                    project=data.get("project", ""),
                    doc_type=data.get("doc_type", ""),
                    similarity=similarity,
                    title=data.get("title", ""),
                )
            )
        return results
