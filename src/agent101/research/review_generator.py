"""文献综述生成器。

根据检索结果与PDF摘要生成结构化的中文综述报告（Markdown）。

Functions:
    generate_review_markdown: 生成综述报告Markdown文本。
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from ..llm import LLMClient


def generate_review_markdown(
    topic: str,
    arxiv_results: Optional[List[Dict[str, str]]] = None,
    semantic_results: Optional[List[Dict[str, str]]] = None,
    pdf_summaries: Optional[List[str]] = None,
) -> str:
    """生成文献综述报告（Markdown）。

    Args:
        topic: 综述主题。
        arxiv_results: arXiv 检索结果列表。
        semantic_results: Semantic Scholar 检索结果列表。
        pdf_summaries: 针对PDF的摘要列表。

    Returns:
        str: Markdown 文本，包含引言、代表性工作、方法比较、应用与局限、结论与参考链接。
    """

    llm = LLMClient()
    context = {
        "topic": topic,
        "arxiv": arxiv_results or [],
        "semantic": semantic_results or [],
        "pdf_summaries": pdf_summaries or [],
    }

    system = (
        "你是资深学术写作者，请基于提供的检索结果与PDF摘要，用中文撰写结构化综述。"
        "输出 Markdown，包含：引言、关键进展、方法比较（可列表）、典型应用、局限与未来方向、结论、参考链接。"
    )
    user = json.dumps(context, ensure_ascii=False)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return llm.chat(messages)