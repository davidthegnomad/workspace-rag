import os
from pathlib import Path

from fnmatch import fnmatch


def resolve_workspace_root() -> Path:
    """Resolve ORGANIZATION root from env or known machine paths."""
    if env := os.environ.get("WORKSPACE_ROOT"):
        return Path(env).expanduser().resolve()

    here = Path(__file__).resolve().parent
    candidates = [
        here.parent.parent.parent,  # .../ORGANIZATION/02_ai_engineering/workspace-rag/internal
        Path("/mnt/SteamDrive/ORGANIZATION"),
        Path.home() / "Desktop/AI Project Folder/ORGANIZATION",
    ]
    for path in candidates:
        if path.is_dir() and (path / "WORKSPACE.md").exists():
            return path.resolve()

    return candidates[0].resolve()


WORKSPACE_ROOT = resolve_workspace_root()

EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIMENSION = 768
OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

FIRESTORE_COLLECTION = os.environ.get(
    "FIRESTORE_COLLECTION", "workspace_rag_internal"
)
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")

MATCH_THRESHOLD = 0.7
DEFAULT_MATCH_COUNT = 10

INDEXED_EXTENSIONS = {".md", ".txt"}

INDEXED_DIRECTORIES = [
    "01_web_design",
    "02_ai_engineering",
    "03_admin_finance",
    "04_business_ops",
    "05_apps_and_extensions",
    "SKILL_LIBRARY",
]

EXCLUDED_DIRECTORIES = {
    "node_modules", ".next", ".venv", "__pycache__", "dist", "build",
    ".firebase", ".git", "VAULT", "06_archive",
}

DOC_TYPE_PATTERNS = {
    "agent_directive": ["**/directives/*.md", "**/AGENTS/*.md", "**/AGENTS.md"],
    "chronicler": ["**/CHRONICLER.md", "**/HANDOFF_*.md"],
    "sop": ["**/SOPS/*.md", "**/workflows/*.md", "**/PROJECT_SOP.md"],
    "skill": ["**/SKILLS/**/*.md"],
    "decision": ["**/DECISIONS/**/*.md"],
    "reference": ["**/references/*.md", "**/KNOWLEDGE_BASE/**/*.md"],
    "client_brief": ["**/Clients/**/*.md", "**/brand-guides/**/*.md"],
    "proposal": ["**/proposals/**/*.md", "**/MARKETING/**/*.md", "**/STRATEGIES/**/*.md"],
    "project_doc": ["**/README.md", "**/ROADMAP.md", "**/TODO.md"],
    "autonomy": ["**/SELF_EVOLUTION.md", "**/SWARM_AUTONOMY_FRAMEWORK.md"],
    "workspace_doc": ["WORKSPACE.md", "MIGRATION_MANIFEST.md", "*.md"],
}


def classify_document(path: Path) -> str:
    rel = str(path.relative_to(WORKSPACE_ROOT))
    for doc_type, patterns in DOC_TYPE_PATTERNS.items():
        for pattern in patterns:
            if fnmatch(rel, pattern):
                return doc_type
    return "general"
