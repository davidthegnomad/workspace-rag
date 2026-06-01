"""Semantic search over the internal Gnomad index."""

from internal.config import (
    DEFAULT_MATCH_COUNT,
    EMBEDDING_MODEL,
    FIREBASE_PROJECT_ID,
    FIRESTORE_COLLECTION,
    MATCH_THRESHOLD,
)
from shared.embeddings import generate_embedding
from shared.store.firestore import FirestoreVectorStore, SearchResult


def get_store() -> FirestoreVectorStore:
    return FirestoreVectorStore(
        collection=FIRESTORE_COLLECTION,
        project_id=FIREBASE_PROJECT_ID or None,
    )


def search(
    query: str,
    threshold: float = MATCH_THRESHOLD,
    limit: int = DEFAULT_MATCH_COUNT,
    filter_metadata: dict | None = None,
) -> list[SearchResult]:
    store = get_store()
    embedding = generate_embedding(query, EMBEDDING_MODEL)
    return store.search(embedding, limit=limit, threshold=threshold, filters=filter_metadata)


def search_by_project(project: str, query: str, **kwargs) -> list[SearchResult]:
    return search(query, filter_metadata={"project": project}, **kwargs)


def search_by_domain(domain: str, query: str, **kwargs) -> list[SearchResult]:
    return search(query, filter_metadata={"domain": domain}, **kwargs)


def search_by_type(doc_type: str, query: str, **kwargs) -> list[SearchResult]:
    return search(query, filter_metadata={"doc_type": doc_type}, **kwargs)
