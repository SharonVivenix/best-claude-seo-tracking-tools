"""Pure helpers for reading a Claude Messages API response that used the web search tool.

No network, no third party imports. Everything here is tested in tests/test_tracker.py.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse


def domain(url: str) -> str:
    host = (urlparse(url).netloc or "").lower()
    return host[4:] if host.startswith("www.") else host


def extract(response: dict) -> dict:
    """Split a Messages API response into answer text, cited URLs and searched URLs.

    Cited URLs come from `citations` on text blocks (web_search_result_location).
    Searched URLs come from web_search_tool_result blocks, which are everything
    Claude retrieved, whether or not it ended up quoting it.
    """
    text_parts: list[str] = []
    cited: list[str] = []
    searched: list[str] = []
    queries = 0
    for block in response.get("content", []):
        kind = block.get("type")
        if kind == "text":
            text_parts.append(block.get("text", ""))
            for c in block.get("citations") or []:
                if c.get("url"):
                    cited.append(c["url"])
        elif kind == "server_tool_use" and block.get("name") == "web_search":
            queries += 1
        elif kind == "web_search_tool_result":
            content = block.get("content")
            if isinstance(content, list):
                searched.extend(r["url"] for r in content if r.get("url"))
    return {
        "text": "".join(text_parts),
        "cited": list(dict.fromkeys(cited)),
        "searched": list(dict.fromkeys(searched)),
        "searches": queries,
    }


def mentions(text: str, aliases: list[str]) -> bool:
    """Whole word, case insensitive. 'Acme' must not match 'Acmeville'."""
    for alias in aliases:
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", text, re.I):
            return True
    return False


def cites(urls: list[str], domains: list[str]) -> bool:
    wanted = {d.lower().removeprefix("www.") for d in domains}
    return any(domain(u) == d or domain(u).endswith("." + d) for u in urls for d in wanted)


def score(parsed: dict, brand: dict, competitors: list[dict]) -> dict:
    text = parsed["text"]
    return {
        "mentioned": mentions(text, brand["aliases"]),
        "cited": cites(parsed["cited"], brand["domains"]),
        "competitors": [c["name"] for c in competitors if mentions(text, c["aliases"])],
        "cited_domains": sorted({domain(u) for u in parsed["cited"]}),
    }
