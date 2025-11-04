"""智能科研助理演示脚本（Week 3）。

流程：
1) 按主题检索 arXiv 与 Semantic Scholar；
2) 对指定 PDF 进行文本抽取与分块摘要；
3) 生成结构化中文综述（Markdown）。

Usage:
    python scripts/demo_research_assistant.py --topic "Graph RAG" --pdf .\samples\paper1.pdf --pdf .\samples\paper2.pdf
"""

from __future__ import annotations

import argparse
from typing import List

from src.agent101.research.academic_search import search_arxiv, search_semantic_scholar
from src.agent101.research.pdf_parser import extract_text_from_pdf, chunk_text, summarize_chunks
from src.agent101.research.review_generator import generate_review_markdown
from src.agent101.logger import get_logger


logger = get_logger("demo-week3")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent 101 Week3 智能科研助理演示")
    parser.add_argument("--topic", type=str, required=True, help="综述主题/关键词")
    parser.add_argument("--pdf", type=str, required=False, action="append", help="PDF路径，可重复")
    parser.add_argument("--max_results", type=int, default=5, help="学术检索返回数")
    parser.add_argument("--max_pages", type=int, default=10, help="PDF最大解析页数")
    args = parser.parse_args()

    topic: str = args.topic
    pdf_paths: List[str] = args.pdf or []

    # 1) 学术检索
    arxiv_results = search_arxiv(topic, max_results=args.max_results)
    semantic_results = search_semantic_scholar(topic, max_results=args.max_results)

    # 2) PDF摘要
    pdf_summaries: List[str] = []
    for path in pdf_paths:
        try:
            text = extract_text_from_pdf(path, max_pages=args.max_pages)
            chunks = chunk_text(text, max_chars=3500)
            summary = summarize_chunks(chunks, instruction=f"主题: {topic}")
            pdf_summaries.append(summary)
        except Exception as exc:
            logger.warning("PDF处理失败 (%s): %s", path, exc)

    # 3) 生成综述
    review_md = generate_review_markdown(
        topic=topic,
        arxiv_results=arxiv_results,
        semantic_results=semantic_results,
        pdf_summaries=pdf_summaries,
    )

    print("\n=== 综述Markdown ===\n")
    print(review_md)


if __name__ == "__main__":
    main()