"""
Embedder module for PakServe AI.
Loads the sentence-transformers model 'all-MiniLM-L6-v2' and generates vector embeddings.
"""

import os
from typing import List, Union
from sentence_transformers import SentenceTransformer

# Model configuration
MODEL_NAME = "all-MiniLM-L6-v2"

# Lazy-loaded model instance singleton
_model_instance = None


def get_model() -> SentenceTransformer:
    """
    Get or initialize the singleton SentenceTransformer model.
    Attempts local cache load first for fast offline execution.

    Returns:
        SentenceTransformer: The loaded embedding model.
    """
    global _model_instance
    if _model_instance is None:
        try:
            # Try loading from local cached weights first without network delay
            _model_instance = SentenceTransformer(MODEL_NAME, local_files_only=True)
        except Exception:
            # Fall back to online loading if not cached locally
            _model_instance = SentenceTransformer(MODEL_NAME)
    return _model_instance


def get_embedding(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """
    Generate embedding vector(s) for the provided text or list of texts.

    Args:
        text (Union[str, List[str]]): Input text string or list of text strings.

    Returns:
        Union[List[float], List[List[float]]]: 384-dimensional embedding vector (or list of vectors).
    """
    model = get_model()
    if isinstance(text, str):
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    elif isinstance(text, list):
        embeddings = model.encode(text, convert_to_numpy=True)
        return embeddings.tolist()
    else:
        raise ValueError("Input must be a string or list of strings.")
