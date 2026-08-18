"""
Generator module for PakServe AI.
Integrates with Google Gemini API (google-genai SDK) to synthesize grounded,
conversational answers from retrieved context chunks with strict anti-hallucination guardrails.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables from backend/.env or root .env
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(BACKEND_DIR.parent / ".env")

# System instruction strictly enforcing grounded responses
SYSTEM_INSTRUCTION = (
    "You are PakServe AI, an assistant that helps users understand Pakistani government service "
    "procedures (NADRA, Passport, Driving License, FBR Tax, Vehicle Registration, and civil documents). "
    "Only answer based on the provided context below. If the context does not contain enough information "
    "to answer the question, say clearly that you don't have verified information on that specific point "
    "and recommend the user check the official source. Do not invent fees, document requirements, or "
    "timelines that are not explicitly present in the context. Keep answers clear, conversational, and "
    "well-organized (use short paragraphs or bullet points where helpful)."
)

# Preferred Flash models with robust multi-tier fallback
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODELS = [
    DEFAULT_MODEL,
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-3.1-flash-lite",
]


def get_genai_client() -> Optional[genai.Client]:
    """
    Initialize and return the Google GenAI Client using GEMINI_API_KEY.

    Returns:
        Optional[genai.Client]: Configured client, or None if API key is missing.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "":
        print("[Generator Warning] GEMINI_API_KEY not found or empty in environment / .env file.")
        return None
    return genai.Client(api_key=api_key.strip())


def build_prompt_context(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Construct formatted context string from retrieved chunks and user query.

    Args:
        user_query (str): The user's question.
        retrieved_chunks (List[Dict[str, Any]]): Retrieved chunks with metadata.

    Returns:
        str: Grounded prompt text for the LLM.
    """
    if not retrieved_chunks:
        context_str = "No relevant procedural documents were retrieved for this query."
    else:
        formatted_chunks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            doc_name = chunk.get("doc_name", "Unknown Document")
            category = chunk.get("category", "General")
            score = chunk.get("similarity_score", 0.0)
            text = chunk.get("text", "").strip()
            formatted_chunks.append(
                f"--- [Document {i}: {doc_name} | Category: {category} | Relevance: {score:.2f}] ---\n{text}"
            )
        context_str = "\n\n".join(formatted_chunks)

    prompt = (
        f"Context from official procedural documents:\n\n"
        f"{context_str}\n\n"
        f"----------------------------------------\n"
        f"User Question: {user_query}\n\n"
        f"Please provide a helpful, clear, and grounded answer based ONLY on the context above."
    )
    return prompt


def generate_answer(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Generate a grounded conversational answer using the Gemini API.

    Args:
        user_query (str): The user's natural language question.
        retrieved_chunks (List[Dict[str, Any]]): List of chunk dicts from vector_store.query().

    Returns:
        str: Generated answer or a graceful fallback message on error.
    """
    client = get_genai_client()
    if client is None:
        return (
            "[Warning] Gemini API Key Missing: Please set GEMINI_API_KEY in backend/.env "
            "to enable AI answer generation."
        )

    prompt = build_prompt_context(user_query, retrieved_chunks)

    seen = set()
    models_to_try = [m for m in FALLBACK_MODELS if not (m in seen or seen.add(m))]

    last_error = None
    for model_candidate in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_candidate,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                ),
            )
            if response and response.text:
                return response.text.strip()
        except APIError as e:
            last_error = e
            print(f"[Generator API Warning] Model {model_candidate} issue ({e.code}): trying next model...", file=sys.stderr)
            continue
        except Exception as e:
            last_error = e
            print(f"[Generator Unexpected Warning] Model {model_candidate} error: {e}, trying next model...", file=sys.stderr)
            continue

    if last_error:
        print(f"[Generator Error] All candidate models exhausted: {last_error}", file=sys.stderr)
        return (
            "I encountered an issue contacting the AI generation service. "
            "Please verify your API key and connection, or check the official departmental portal directly."
        )

    return "I apologize, but I could not generate an answer based on the provided records."
