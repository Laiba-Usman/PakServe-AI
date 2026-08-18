"""
Chunker module for PakServe AI.
Implements word-based overlapping text chunking to preserve context across boundaries.
"""

from typing import List


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    Split text into word-based chunks with a specified overlap.

    Args:
        text (str): Raw document text.
        chunk_size (int): Maximum number of words per chunk. Defaults to 300.
        overlap (int): Number of overlapping words between consecutive chunks. Defaults to 50.

    Returns:
        List[str]: List of text chunks.
    """
    if not text or not text.strip():
        return []

    words = text.strip().split()
    if not words:
        return []

    if len(words) <= chunk_size:
        return [" ".join(words)]

    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size  # Fallback to avoid infinite loops if overlap >= chunk_size

    chunks = []
    for i in range(0, len(words), step):
        chunk_words = words[i : i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        # If the current chunk reaches the end of the text, break
        if i + chunk_size >= len(words):
            break

    return chunks
