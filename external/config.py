import os
from pathlib import Path

import yaml

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_DIMENSION = 768
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MATCH_THRESHOLD = 0.7
DEFAULT_MATCH_COUNT = 10

FIRESTORE_COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "workspace_rag_external")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")

INDEXED_EXTENSIONS = {".md", ".txt"}
EXCLUDED_DIR_NAMES = {
    "node_modules", ".git", ".venv", "__pycache__", "dist", "build", ".next",
}


def load_config(config_path: Path | None = None) -> dict:
    path = config_path or Path(__file__).parent / "config.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_workspace_root(cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    if env := os.environ.get("WORKSPACE_ROOT"):
        return Path(env).expanduser().resolve()
    if root := cfg.get("workspace_root"):
        return Path(root).expanduser().resolve()
    return Path.cwd().resolve()


def get_settings(config_path: Path | None = None) -> dict:
    cfg = load_config(config_path)
    return {
        "workspace_root": resolve_workspace_root(cfg),
        "embedding_model": cfg.get("embedding_model", EMBEDDING_MODEL),
        "chunk_size": cfg.get("chunk_size", CHUNK_SIZE),
        "chunk_overlap": cfg.get("chunk_overlap", CHUNK_OVERLAP),
        "firestore_collection": cfg.get("firestore_collection", FIRESTORE_COLLECTION),
        "indexed_extensions": set(cfg.get("indexed_extensions", INDEXED_EXTENSIONS)),
        "excluded_dirs": set(cfg.get("excluded_dirs", EXCLUDED_DIR_NAMES)),
    }
