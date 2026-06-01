from pathlib import Path


def discover_documents(root: Path, extensions: set[str], excluded: set[str]) -> list[Path]:
    documents = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in extensions:
            continue
        if any(part in excluded for part in path.parts):
            continue
        documents.append(path)
    return sorted(documents)


def extract_metadata(path: Path, root: Path) -> dict:
    rel = path.relative_to(root)
    parts = list(rel.parts)
    return {
        "source_path": str(rel),
        "domain": parts[0] if parts else "root",
        "project": parts[1] if len(parts) > 1 else "root",
        "doc_type": "general",
        "title": path.stem.replace("_", " ").replace("-", " "),
    }
