"""PDF 解析与摘要模块。

提供从 PDF 提取文本、分块与摘要的能力，适用于大文档处理。

Functions:
    extract_text_from_pdf: 从 PDF 文件提取纯文本。
    chunk_text: 将长文本按字符限制分块。
    summarize_chunks: 使用 LLM 对分块文本进行摘要并合并。
"""

from __future__ import annotations

from typing import List, Optional

from pypdf import PdfReader

from ..llm import LLMClient


def extract_text_from_pdf(pdf_path: str, max_pages: Optional[int] = None) -> str:
    """提取 PDF 文本。

    Args:
        pdf_path: PDF 文件路径。
        max_pages: 最大解析页数，None 表示解析全部。

    Returns:
        str: 提取的纯文本内容。

    Raises:
        RuntimeError: 当文件无法打开或解析失败时抛出。
    """

    try:
        reader = PdfReader(pdf_path)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"无法读取PDF: {exc}")

    pages_to_read = len(reader.pages) if max_pages is None else min(max_pages, len(reader.pages))
    texts: List[str] = []
    for i in range(pages_to_read):
        try:
            page = reader.pages[i]
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return "\n\n".join(texts).strip()


def chunk_text(text: str, max_chars: int = 4000) -> List[str]:
    """按字符限制分块长文本。

    Args:
        text: 原始文本。
        max_chars: 每块最大字符数。

    Returns:
        List[str]: 文本分块列表。
    """

    chunks: List[str] = []
    cursor = 0
    while cursor < len(text):
        end = min(cursor + max_chars, len(text))
        chunks.append(text[cursor:end])
        cursor = end
    return chunks


def summarize_chunks(chunks: List[str], instruction: Optional[str] = None) -> str:
    """对文本分块进行摘要并合并。

    Args:
        chunks: 文本分块列表。
        instruction: 额外的摘要指令，例如“聚焦方法与结论”。

    Returns:
        str: 合并后的最终摘要文本。

    Raises:
        RuntimeError: 当 LLM 请求失败或返回为空。
    """

    llm = LLMClient()
    summaries: List[str] = []
    for idx, c in enumerate(chunks):
        sys_prompt = "你是学术助手，请用中文总结下面的论文内容，突出贡献点、方法与结论。"
        if instruction:
            sys_prompt += f" 指令: {instruction}"
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"第 {idx+1} 段内容如下：\n{c}"},
        ]
        summary = llm.chat(messages)
        summaries.append(summary)

    # 二次汇总
    final_messages = [
        {"role": "system", "content": "将多段摘要融合为一段结构化中文摘要，包含背景、方法、结果与局限。"},
        {"role": "user", "content": "\n\n".join(summaries)},
    ]
    return llm.chat(final_messages)