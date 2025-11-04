"""DuckDuckGo 搜索工具。

基于 `duckduckgo-search` 包进行简单的 Web 搜索，返回标题与链接。

Functions:
    web_search: 执行搜索并返回若干条结果。

Raises:
    RuntimeError: 当搜索请求失败时抛出。
"""

from __future__ import annotations

from typing import Dict, List

from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """执行 Web 搜索。

    Args:
        query: 搜索关键词。
        max_results: 返回结果数量，默认 5。

    Returns:
        List[Dict[str, str]]: 每项包含 `title` 与 `link`。

    Raises:
        RuntimeError: 当底层搜索失败。
    """

    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"搜索失败: {exc}")

    mapped: List[Dict[str, str]] = []
    for item in results or []:
        mapped.append({"title": item.get("title", ""), "link": item.get("href", "")})
    return mapped