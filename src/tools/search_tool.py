"""
Web search tool. Uses Tavily if TAVILY_API_KEY is set; otherwise returns a
stub so the rest of the system works without it.

Swap this file for any other search backend (Brave, SerpAPI, etc.) —
the function signature is the contract the agents depend on.
"""

import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_URL = "https://api.tavily.com/search"


def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web and return a list of results.

    Returns:
        {
          "query": str,
          "results": [{"title": str, "url": str, "snippet": str}, ...]
        }
    On error or missing key returns results=[] with an explanatory note.
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "query": query,
            "note": (
                "Web search is disabled — TAVILY_API_KEY not set. "
                "FRED data tools are fully functional. "
                "Add a Tavily key to .env to enable web search."
            ),
            "results": [],
        }

    try:
        resp = requests.post(
            TAVILY_URL,
            json={"api_key": api_key, "query": query, "max_results": max_results},
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json().get("results", [])
        return {
            "query": query,
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": (r.get("content") or "")[:400],
                }
                for r in raw
            ],
        }
    except requests.RequestException as exc:
        return {"query": query, "error": str(exc), "results": []}
