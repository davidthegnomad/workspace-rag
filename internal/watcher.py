"""Watch Gnomad ORGANIZATION for markdown changes and delta re-index."""

import time
from pathlib import Path

from rich.console import Console
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from internal.config import EXCLUDED_DIRECTORIES, INDEXED_DIRECTORIES, INDEXED_EXTENSIONS, WORKSPACE_ROOT
from internal.indexer import get_store, index_document

console = Console()


class WorkspaceHandler(FileSystemEventHandler):
    def __init__(self, store):
        self.store = store
        self.stats = {"docs_indexed": 0, "chunks_indexed": 0, "skipped": 0, "errors": []}

    def _should_index(self, path: str) -> bool:
        p = Path(path)
        if p.suffix not in INDEXED_EXTENSIONS:
            return False
        if any(excluded in p.parts for excluded in EXCLUDED_DIRECTORIES):
            return False
        try:
            rel = p.relative_to(WORKSPACE_ROOT)
            domain = rel.parts[0] if rel.parts else ""
            return domain in INDEXED_DIRECTORIES or p.parent == WORKSPACE_ROOT
        except ValueError:
            return False

    def _remove(self, path: str) -> None:
        try:
            rel = str(Path(path).relative_to(WORKSPACE_ROOT))
            count = self.store.delete_by_source_path(rel)
            console.print(f"[yellow]Removed {count} chunks for: {rel}[/yellow]")
        except Exception as e:
            console.print(f"[red]Error removing chunks: {e}[/red]")

    def on_modified(self, event):
        if event.is_directory or not self._should_index(event.src_path):
            return
        console.print(f"[blue]Re-indexing: {event.src_path}[/blue]")
        index_document(Path(event.src_path), self.store, self.stats)

    def on_created(self, event):
        if event.is_directory or not self._should_index(event.src_path):
            return
        console.print(f"[green]Indexing new: {event.src_path}[/green]")
        index_document(Path(event.src_path), self.store, self.stats)

    def on_deleted(self, event):
        if event.is_directory or not self._should_index(event.src_path):
            return
        self._remove(event.src_path)


def run_watcher() -> None:
    console.print(f"[bold]Watching {WORKSPACE_ROOT} for changes...[/bold]")
    store = get_store()
    handler = WorkspaceHandler(store)
    observer = Observer()

    for domain in INDEXED_DIRECTORIES:
        domain_path = WORKSPACE_ROOT / domain
        if domain_path.exists():
            observer.schedule(handler, str(domain_path), recursive=True)
            console.print(f"  Watching: {domain}")

    observer.schedule(handler, str(WORKSPACE_ROOT), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[bold]Watcher stopped.[/bold]")
    observer.join()
