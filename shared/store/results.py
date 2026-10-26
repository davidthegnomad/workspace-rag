from dataclasses import dataclass


@dataclass
class SearchResult:
    content: str
    source_path: str
    domain: str
    project: str
    doc_type: str
    similarity: float
    title: str

    def __str__(self) -> str:
        return (
            f"[{self.similarity:.2f}] {self.source_path}\n"
            f"  Type: {self.doc_type} | Project: {self.project}\n"
            f"  {self.content[:200]}..."
        )
