import ollama


def generate_embedding(text: str, model: str = "nomic-embed-text") -> list[float]:
    """Generate embedding vector via Ollama."""
    response = ollama.embed(model=model, input=text)
    return response["embeddings"][0]
