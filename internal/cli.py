"""CLI for the internal Gnomad workspace RAG pipeline."""

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
    """Gnomad Internal RAG — semantic search across ORGANIZATION."""
    pass


@cli.command()
def index():
    """Run a full workspace index."""
    from internal.indexer import run_full_index
    run_full_index()


@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=10, help="Max results")
@click.option("--threshold", "-t", default=0.7, help="Similarity threshold (0–1)")
@click.option("--project", "-p", default=None, help="Filter by project")
@click.option("--domain", "-d", default=None, help="Filter by domain")
@click.option("--type", "doc_type", default=None, help="Filter by doc type")
def search(query, limit, threshold, project, domain, doc_type):
    """Semantic search across indexed documents."""
    from internal.query import search as do_search, search_by_domain, search_by_project, search_by_type

    if project:
        results = search_by_project(project, query, limit=limit, threshold=threshold)
    elif domain:
        results = search_by_domain(domain, query, limit=limit, threshold=threshold)
    elif doc_type:
        results = search_by_type(doc_type, query, limit=limit, threshold=threshold)
    else:
        results = do_search(query, limit=limit, threshold=threshold)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(title=f"Results for: {query}")
    table.add_column("Score", width=6)
    table.add_column("Source", style="cyan")
    table.add_column("Type", width=16)
    table.add_column("Preview", max_width=60)

    for r in results:
        preview = r.content[:120].replace("\n", " ")
        table.add_row(f"{r.similarity:.2f}", r.source_path, r.doc_type, preview)

    console.print(table)


@cli.command()
def status():
    """Show index statistics."""
    from internal.config import FIRESTORE_COLLECTION, WORKSPACE_ROOT
    from internal.indexer import get_store

    store = get_store()
    total = store.count()

    console.print("\n[bold]Gnomad Internal RAG Status[/bold]")
    console.print(f"  Workspace: [cyan]{WORKSPACE_ROOT}[/cyan]")
    console.print(f"  Collection: [cyan]{FIRESTORE_COLLECTION}[/cyan]")
    console.print(f"  Total chunks indexed: [green]{total}[/green]")

    if total > 0:
        table = Table(title="Chunks by Domain")
        table.add_column("Domain")
        table.add_column("Chunks", justify="right")
        for row in store.domain_stats():
            table.add_row(str(row["domain"]), str(row["count"]))
        console.print(table)


@cli.command()
def watch():
    """Start the file watcher for auto-reindexing."""
    from internal.watcher import run_watcher
    run_watcher()


@cli.command()
def clear():
    """Clear the entire index (destructive!)."""
    from internal.indexer import get_store

    if not click.confirm("This will delete ALL indexed documents. Continue?"):
        return
    deleted = get_store().clear_all()
    console.print(f"[green]Index cleared ({deleted} chunks removed).[/green]")


if __name__ == "__main__":
    cli()
