"""Index user workspace documents into Firestore (external product)."""

import hashlib
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from external.config import get_settings
from external.discover import discover_documents, extract_metadata
from shared.chunking import chunk_document
from shared.embeddings import generate_embedding
from shared.store.firestore import FirestoreVectorStore


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def get_store(settings: dict) -> FirestoreVectorStore:
    from external.config import FIREBASE_PROJECT_ID
    return FirestoreVectorStore(
        collection=settings["firestore_collection"],
        project_id=FIREBASE_PROJECT_ID or None,
    )


def index_document(path: Path, root: Path, store: FirestoreVectorStore, settings: dict, stats: dict) -> None:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        stats["errors"].append(f"{path}: {e}")
        return

    if not content.strip():
        stats["skipped"] += 1
        return

    metadata = extract_metadata(path, root)
    store.delete_by_source_path(metadata["source_path"])
    chunks = chunk_document(content, settings["chunk_size"], settings["chunk_overlap"])
    model = settings["embedding_model"]

    for i, chunk in enumerate(chunks):
        record = {
            **metadata,
            "content": chunk,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "content_hash": content_hash(chunk),
            "embedding": generate_embedding(chunk, model),
        }
        try:
            store.upsert_chunk(record)
            stats["chunks_indexed"] += 1
        except Exception as e:
            stats["errors"].append(f"{path} chunk {i}: {e}")

    stats["docs_indexed"] += 1


def run_full_index(config_path: Path | None = None) -> None:
    console = Console()
    settings = get_settings(config_path)
    root = settings["workspace_root"]
    store = get_store(settings)

    console.print(f"[bold]Workspace root:[/bold] {root}")
    documents = discover_documents(root, settings["indexed_extensions"], settings["excluded_dirs"])
    console.print(f"Found [green]{len(documents)}[/green] documents to index")

    stats = {"docs_indexed": 0, "chunks_indexed": 0, "skipped": 0, "errors": []}
    with Progress() as progress:
        task = progress.add_task("Indexing...", total=len(documents))
        for doc in documents:
            index_document(doc, root, store, settings, stats)
            progress.advance(task)

    console.print("\n[bold green]Indexing complete![/bold green]")
    console.print(f"  Documents: {stats['docs_indexed']}")
    console.print(f"  Chunks: {stats['chunks_indexed']}")
    if stats["errors"]:
        console.print(f"  [red]Errors: {len(stats['errors'])}[/red]")
