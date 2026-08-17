"""
Thin wrappers around Tavily (search) and requests (fetch) so the agent
graph doesn't need to know API details. Requires TAVILY_API_KEY in env.
"""
from __future__ import annotations
import os
import re
from typing import Optional, List, Dict, Any
import requests
from tavily import TavilyClient  # type: ignore  # pyrefly: ignore [missing-import]

_tavily: Optional[TavilyClient] = None


def get_tavily() -> TavilyClient:
    global _tavily
    if _tavily is None:
        if os.path.exists(".env"):
            with open(".env", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        os.environ[k] = v.strip().strip('"').strip("'")
        key = os.environ.get("TAVILY_API_KEY")

        if not key:
            raise RuntimeError("TAVILY_API_KEY not set in environment")
        _tavily = TavilyClient(api_key=key)
    return _tavily


def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Returns list of {title, url, content} snippets."""
    client = get_tavily()
    resp: Dict[str, Any] = client.search(query=query, max_results=max_results, search_depth="advanced") # type: ignore
    results = resp.get("results", []) if isinstance(resp, dict) else []
    return [
        {
            "title": str(r.get("title", "")) if isinstance(r, dict) else "",
            "url": str(r.get("url", "")) if isinstance(r, dict) else "",
            "content": str(r.get("content", "")) if isinstance(r, dict) else "",
        }
        for r in results
    ]


def fetch_page_text(url: str, max_chars: int = 8000) -> str:
    """Best-effort raw fetch + text extraction for a docs page.

    Strategy:
    1. First try Tavily extract (renders JS, better for SPAs)
    2. Fall back to direct HTTP fetch with HTML stripping
    3. Falls back gracefully — some docs sites block bots, agent should
       treat empty result as low confidence, not crash.
    """
    # Strategy 1: Use Tavily's extract for JS-rendered pages
    try:
        client = get_tavily()
        if hasattr(client, "extract"):
            result: Any = client.extract(urls=[url])
            if isinstance(result, dict) and result.get("results"):
                res_list = result["results"]
                if res_list and isinstance(res_list[0], dict):
                    text = res_list[0].get("raw_content", "")
                    if text and len(str(text).strip()) > 100:
                        return str(text)[:max_chars]
    except Exception:
        pass  # fall through to direct fetch

    # Strategy 2: Direct HTTP fetch with improved text extraction
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        r.raise_for_status()
        text = r.text
        # Remove script and style blocks
        text = re.sub(r"<script.*?</script>", " ", text, flags=re.S)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
        # Remove HTML comments
        text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
        # Remove nav, header, footer elements (often noise)
        text = re.sub(r"<(nav|header|footer).*?</\1>", " ", text, flags=re.S)
        # Replace tags with spaces
        text = re.sub(r"<[^>]+>", " ", text)
        # Clean up HTML entities
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        text = re.sub(r"&#\d+;", " ", text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 100:  # got meaningful content
            return text[:max_chars]
        return f"[FETCH_FAILED: page returned minimal text content ({len(text)} chars)]"
    except Exception as e:
        return f"[FETCH_FAILED: {e}]"
