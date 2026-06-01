from datetime import datetime, timezone
from pathlib import Path

from internal.config import (
    EXCLUDED_DIRECTORIES,
    INDEXED_DIRECTORIES,
    INDEXED_EXTENSIONS,
    WORKSPACE_ROOT,
    classify_document,
)


def discover_documents(root: Path = WORKSPACE_ROOT) -> list[Path]:
    """Walk the Gnomad ORGANIZATION workspace and find indexable documents."""
    documents = []
    for domain_dir in INDEXED_DIRECTORIES:
        domain_path = root / domain_dir
        if not domain_path.exists():
            continue
        for path in domain_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in INDEXED_EXTENSIONS:
                continue
            if any(excluded in path.parts for excluded in EXCLUDED_DIRECTORIES):
                continue
            documents.append(path)

    for root_doc in root.glob("*.md"):
        if root_doc.is_file():
            documents.append(root_doc)

    return sorted(set(documents))


def extract_metadata(path: Path) -> dict:
    rel = path.relative_to(WORKSPACE_ROOT)
    parts = list(rel.parts)
    domain = parts[0] if parts else "root"
    project = parts[1] if len(parts) > 1 else "root"
    stat = path.stat()
    return {
        "source_path": str(rel),
        "domain": domain,
        "project": project,
        "doc_type": classify_document(path),
        "title": path.stem.replace("_", " ").replace("-", " "),
        "last_modified": datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).isoformat(),
        "file_size": stat.st_size,
    }
