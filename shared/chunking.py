import tiktoken


def _overlap_tail(words: list[str], overlap: int, enc) -> list[str]:
    if overlap <= 0 or not words:
        return []
    kept = []
    tokens = 0
    for word in reversed(words):
        word_tokens = len(enc.encode(word))
        if kept and tokens + word_tokens > overlap:
            break
        kept.append(word)
        tokens += word_tokens
    kept.reverse()
    return kept


def chunk_document(
    content: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split content into semantic chunks based on markdown headers and token count."""
    enc = tiktoken.get_encoding("cl100k_base")

    sections = []
    current_section = []
    for line in content.split("\n"):
        if line.startswith("#") and current_section:
            sections.append("\n".join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    if current_section:
        sections.append("\n".join(current_section))

    chunks = []
    current_chunk = []
    current_tokens = 0

    for section in sections:
        section_tokens = len(enc.encode(section))
        if section_tokens > chunk_size:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            words = section.split()
            sub_chunk = []
            sub_tokens = 0
            for word in words:
                word_tokens = len(enc.encode(word))
                if sub_tokens + word_tokens > chunk_size and sub_chunk:
                    chunks.append(" ".join(sub_chunk))
                    sub_chunk = _overlap_tail(sub_chunk, overlap, enc)
                    sub_tokens = len(enc.encode(" ".join(sub_chunk))) if sub_chunk else 0
                sub_chunk.append(word)
                sub_tokens += word_tokens
            if sub_chunk:
                chunks.append(" ".join(sub_chunk))
        elif current_tokens + section_tokens > chunk_size:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [section]
            current_tokens = section_tokens
        else:
            current_chunk.append(section)
            current_tokens += section_tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return [c.strip() for c in chunks if c.strip()]
