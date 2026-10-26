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


def load_settings(config, root):
    from external.config import get_settings

    settings = get_settings(Path(config) if config else None)
    if root:
        settings["workspace_root"] = Path(root).expanduser().resolve()
        if settings.get("store") != "firestore":
            settings["index_path"] = settings["workspace_root"] / ".workspace-rag" / "index.sqlite"
    return settings


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), default=None, help="Path to config.yaml")
@click.option("--root", type=click.Path(exists=True, file_okay=False), default=None, help="Folder to index")
def index(config, root):
    """Index documents from configured workspace root."""
    from external.indexer import run_full_index
    run_full_index(Path(config) if config else None, root=Path(root) if root else None)


@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=10)
@click.option("--threshold", "-t", default=0.7)
@click.option("--config", "-c", type=click.Path(exists=True), default=None)
@click.option("--root", type=click.Path(exists=True, file_okay=False), default=None, help="Folder that was indexed")
def search(query, limit, threshold, config, root):
    """Semantic search over indexed documents."""
    from external.store import open_store
    from shared.embeddings import generate_embedding

    settings = load_settings(config, root)
    store = open_store(settings)
    embedding = generate_embedding(query, settings["embedding_model"])
    results = store.search(embedding, limit=limit, threshold=threshold, query_text=query)

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
@click.option("--root", type=click.Path(exists=True, file_okay=False), default=None)
def status(config, root):
    """Show index statistics."""
    from external.store import open_store

    settings = load_settings(config, root)
    store = open_store(settings)
    total = store.count()
    console.print("\n[bold]Workspace RAG[/bold]")
    console.print(f"  Folder: [cyan]{settings['workspace_root']}[/cyan]")
    console.print(f"  Store: [cyan]{settings['store']}[/cyan]")
    if settings["store"] == "sqlite":
        console.print(f"  Index: [cyan]{settings['index_path']}[/cyan]")
    else:
        console.print(f"  Collection: [cyan]{settings['firestore_collection']}[/cyan]")
    console.print(f"  Chunks: [green]{total}[/green]")


if __name__ == "__main__":
    cli()
