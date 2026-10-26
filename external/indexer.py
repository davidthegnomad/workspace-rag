"""Index a folder of notes. SQLite by default. Firestore only when config says so."""

import hashlib
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from external.config import get_settings
from external.discover import discover_documents, extract_metadata
from external.store import open_store
from shared.chunking import chunk_document
from shared.embeddings import generate_embedding


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def index_document(path: Path, root: Path, store, settings: dict, stats: dict) -> None:
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


def run_full_index(config_path: Path | None = None, root: Path | None = None) -> None:
    console = Console()
    settings = get_settings(config_path)
    if root is not None:
        settings["workspace_root"] = Path(root).expanduser().resolve()
        if settings.get("store") != "firestore":
            settings["index_path"] = settings["workspace_root"] / ".workspace-rag" / "index.sqlite"
    root = settings["workspace_root"]
    store = open_store(settings)

    console.print(f"[bold]Folder:[/bold] {root}")
    if settings.get("store") == "sqlite":
        console.print(f"[bold]Index:[/bold] {settings['index_path']}")
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
