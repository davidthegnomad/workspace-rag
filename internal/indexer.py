"""Index Gnomad ORGANIZATION documents into Firestore."""

import hashlib
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from internal.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    FIREBASE_PROJECT_ID,
    FIRESTORE_COLLECTION,
)
from internal.discover import discover_documents, extract_metadata
from shared.chunking import chunk_document
from shared.embeddings import generate_embedding
from shared.store.firestore import FirestoreVectorStore


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def get_store() -> FirestoreVectorStore:
    return FirestoreVectorStore(
        collection=FIRESTORE_COLLECTION,
        project_id=FIREBASE_PROJECT_ID or None,
    )


def index_document(path: Path, store: FirestoreVectorStore, stats: dict) -> None:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        stats["errors"].append(f"{path}: {e}")
        return

    if not content.strip():
        stats["skipped"] += 1
        return

    metadata = extract_metadata(path)
    store.delete_by_source_path(metadata["source_path"])
    chunks = chunk_document(content, CHUNK_SIZE, CHUNK_OVERLAP)

    for i, chunk in enumerate(chunks):
        record = {
            **metadata,
            "content": chunk,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "content_hash": content_hash(chunk),
            "embedding": generate_embedding(chunk, EMBEDDING_MODEL),
        }
        try:
            store.upsert_chunk(record)
            stats["chunks_indexed"] += 1
        except Exception as e:
            stats["errors"].append(f"{path} chunk {i}: {e}")

    stats["docs_indexed"] += 1


def run_full_index() -> None:
    console = Console()
    store = get_store()

    from internal.config import WORKSPACE_ROOT
    console.print(f"[bold]Workspace root:[/bold] {WORKSPACE_ROOT}")

    console.print("[bold]Discovering documents...[/bold]")
    documents = discover_documents()
    console.print(f"Found [green]{len(documents)}[/green] documents to index")

    stats = {"docs_indexed": 0, "chunks_indexed": 0, "skipped": 0, "errors": []}

    with Progress() as progress:
        task = progress.add_task("Indexing...", total=len(documents))
        for doc in documents:
            index_document(doc, store, stats)
            progress.advance(task)

    console.print("\n[bold green]Indexing complete![/bold green]")
    console.print(f"  Documents: {stats['docs_indexed']}")
    console.print(f"  Chunks: {stats['chunks_indexed']}")
    console.print(f"  Skipped: {stats['skipped']}")
    if stats["errors"]:
        console.print(f"  [red]Errors: {len(stats['errors'])}[/red]")
        for err in stats["errors"][:10]:
            console.print(f"    {err}")
