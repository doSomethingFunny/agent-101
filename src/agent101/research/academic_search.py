"""学术数据库检索模块。

封装 arXiv 与 Semantic Scholar 的检索接口，返回统一结构的数据。

Functions:
    search_arxiv: 按关键词检索 arXiv 论文。
    search_semantic_scholar: 按关键词检索 Semantic Scholar 文献。
"""

from __future__ import annotations

from typing import Dict, List

import arxiv
from semanticscholar import SemanticScholar

from ..config import load_settings


def search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """检索 arXiv 文献。

    Args:
        query: 关键词。
        max_results: 返回数量。

    Returns:
        List[Dict[str, str]]: 每项包含 `title`, `summary`, `link`。
    """

    results: List[Dict[str, str]] = []
    try:
        search = arxiv.Search(query=query, max_results=max_results)
        for r in search.results():
            results.append(
                {
                    "title": r.title,
                    "summary": r.summary,
                    "link": r.entry_id,
                }
            )
    except Exception:
        # 静默失败，返回空列表
        return []
    return results


def search_semantic_scholar(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """检索 Semantic Scholar 文献。

    Args:
        query: 关键词。
        max_results: 返回数量。

    Returns:
        List[Dict[str, str]]: 每项包含 `title`, `abstract`, `link`。
    """

    settings = load_settings()
    api_key = getattr(settings, "semantic_scholar_api_key", None)
    client = SemanticScholar(api_key=api_key) if api_key else SemanticScholar()

    results: List[Dict[str, str]] = []
    try:
        papers = client.search_paper(query=query, limit=max_results)
        for p in papers or []:
            results.append(
                {
                    "title": p.get("title", ""),
                    "abstract": p.get("abstract", ""),
                    "link": p.get("url", ""),
                }
            )
    except Exception:
        return []
    return results