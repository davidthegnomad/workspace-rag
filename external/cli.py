"""CLI for the external distributable RAG product."""

import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

console = Console()


@click.group()
def cli():
    """Workspace RAG External — semantic search for any document folder."""
    pass


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), default=None, help="Path to config.yaml")
def index(config):
    """Index documents from configured workspace root."""
    from external.indexer import run_full_index
    run_full_index(Path(config) if config else None)


@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=10)
@click.option("--threshold", "-t", default=0.7)
@click.option("--config", "-c", type=click.Path(exists=True), default=None)
def search(query, limit, threshold, config):
    """Semantic search over indexed documents."""
    from external.config import get_settings
    from external.config import FIREBASE_PROJECT_ID
    from shared.embeddings import generate_embedding
    from shared.store.firestore import FirestoreVectorStore

    settings = get_settings(Path(config) if config else None)
    store = FirestoreVectorStore(settings["firestore_collection"], FIREBASE_PROJECT_ID or None)
    embedding = generate_embedding(query, settings["embedding_model"])
    results = store.search(embedding, limit=limit, threshold=threshold)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(title=f"Results for: {query}")
    table.add_column("Score", width=6)
    table.add_column("Source", style="cyan")
    table.add_column("Preview", max_width=60)
    for r in results:
        table.add_row(f"{r.similarity:.2f}", r.source_path, r.content[:120].replace("\n", " "))
    console.print(table)


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), default=None)
def status(config):
    """Show index statistics."""
    from external.config import get_settings, FIREBASE_PROJECT_ID
    from shared.store.firestore import FirestoreVectorStore

    settings = get_settings(Path(config) if config else None)
    store = FirestoreVectorStore(settings["firestore_collection"], FIREBASE_PROJECT_ID or None)
    total = store.count()
    console.print(f"\n[bold]External RAG Status[/bold]")
    console.print(f"  Workspace: [cyan]{settings['workspace_root']}[/cyan]")
    console.print(f"  Collection: [cyan]{settings['firestore_collection']}[/cyan]")
    console.print(f"  Chunks: [green]{total}[/green]")


if __name__ == "__main__":
    cli()
