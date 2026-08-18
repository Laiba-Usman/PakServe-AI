"""
Analytics module for PakServe AI.
Logs search queries, timestamps, top retrieved documents, and categories to persistent CSV storage.
Provides aggregation functions for the analytics dashboard.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
LOGS_FILE = DATA_DIR / "search_logs.csv"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# CSV Header schema
CSV_COLUMNS = ["timestamp", "query", "top_result_doc", "category"]


def init_log_file() -> None:
    """Initialize CSV log file with header if it does not exist."""
    if not LOGS_FILE.exists():
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(LOGS_FILE, index=False)


def log_search(
    query: str,
    top_result_doc: Optional[str] = None,
    category: Optional[str] = None,
    timestamp: Optional[str] = None
) -> None:
    """
    Append a search query event to persistent CSV logs.

    Args:
        query (str): The search query text.
        top_result_doc (Optional[str]): Document name of the top retrieved chunk.
        category (Optional[str]): Category of the top result.
        timestamp (Optional[str]): ISO timestamp string. Defaults to current UTC/local time.
    """
    init_log_file()

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    new_row = {
        "timestamp": timestamp,
        "query": query.strip(),
        "top_result_doc": top_result_doc or "None",
        "category": category or "General"
    }

    df_new = pd.DataFrame([new_row])
    df_new.to_csv(LOGS_FILE, mode="a", header=not LOGS_FILE.exists(), index=False)


def get_analytics() -> Dict[str, Any]:
    """
    Calculate and return aggregate analytics metrics from search logs.

    Returns:
        Dict[str, Any]: Analytics report containing:
            - total_searches (int)
            - top_queries (List[Dict[str, Any]])
            - category_usage (Dict[str, int])
            - most_retrieved_documents (List[Dict[str, Any]])
            - recent_searches (List[Dict[str, Any]])
    """
    init_log_file()

    if not LOGS_FILE.exists() or os.path.getsize(LOGS_FILE) == 0:
        return {
            "total_searches": 0,
            "top_queries": [],
            "category_usage": {},
            "most_retrieved_documents": [],
            "recent_searches": []
        }

    try:
        df = pd.read_csv(LOGS_FILE)
    except Exception as e:
        print(f"[Analytics Error] Failed reading log CSV: {e}")
        return {
            "total_searches": 0,
            "top_queries": [],
            "category_usage": {},
            "most_retrieved_documents": [],
            "recent_searches": []
        }

    if df.empty:
        return {
            "total_searches": 0,
            "top_queries": [],
            "category_usage": {},
            "most_retrieved_documents": [],
            "recent_searches": []
        }

    total_searches = len(df)

    # Top Queries
    top_queries_counts = df["query"].value_counts().head(10)
    top_queries = [
        {"query": q, "count": int(c)}
        for q, c in top_queries_counts.items()
    ]

    # Category Usage
    category_counts = df["category"].value_counts().to_dict()
    category_usage = {str(k): int(v) for k, v in category_counts.items()}

    # Most Retrieved Documents
    valid_docs = df[df["top_result_doc"] != "None"]
    if not valid_docs.empty:
        top_docs_counts = valid_docs["top_result_doc"].value_counts().head(10)
        most_retrieved_docs = [
            {"doc_name": doc, "count": int(count)}
            for doc, count in top_docs_counts.items()
        ]
    else:
        most_retrieved_docs = []

    # Recent Searches (last 10)
    recent_records = df.tail(10).to_dict(orient="records")
    recent_searches = list(reversed(recent_records))

    return {
        "total_searches": total_searches,
        "top_queries": top_queries,
        "category_usage": category_usage,
        "most_retrieved_documents": most_retrieved_docs,
        "recent_searches": recent_searches
    }
