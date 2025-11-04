"""文件处理Agent。

职责：
- 分类文件类型（PDF/Word/Excel/Text）。
- 调用对应抽取器生成结构化信息与摘要。
- 执行简单实体抽取（URL、Email、日期）。
- 生成中文Markdown报告（可选）。

Classes:
    FileAgent: 提供 `analyze` 与 `generate_markdown` 两个主要方法。
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from ..logger import get_logger
from ..llm import LLMClient
from .classifier import classify_file_type, FileType
from .extractors import (
    extract_pdf_summary,
    extract_word_text,
    summarize_text,
    extract_excel_overview,
)


logger = get_logger(__name__)


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://[\w\-._~:/?#@!$&'()*+,;=%]+")
DATE_RE = re.compile(r"\b(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})\b")


class FileAgent:
    """文件处理Agent，提供统一分析入口。"""

    def analyze(self, file_path: str, max_preview_rows: int = 5) -> Dict[str, Any]:
        """分析文件并返回结构化结果。

        Args:
            file_path: 文件路径。
            max_preview_rows: Excel示例行上限。

        Returns:
            Dict[str, Any]: 包含 `file_type`、`overview`、`entities`、`errors` 等字段。
        """

        result: Dict[str, Any] = {
            "file_path": file_path,
            "file_type": "unknown",
            "overview": {},
            "entities": {"urls": [], "emails": [], "dates": []},
            "errors": [],
        }

        if not os.path.exists(file_path):
            result["errors"].append("文件不存在")
            return result

        ftype: FileType = classify_file_type(file_path)
        result["file_type"] = ftype

        try:
            if ftype == "pdf":
                pdf = extract_pdf_summary(file_path)
                result["overview"] = {"type": "pdf", **pdf}
                # 实体抽取基于摘要与摘录
                text_for_entities = (pdf.get("summary", "") + "\n" + pdf.get("text_excerpt", ""))
                result["entities"] = _extract_entities(text_for_entities)
            elif ftype == "word":
                text = extract_word_text(file_path)
                summary = summarize_text(text)
                result["overview"] = {"type": "word", "text_excerpt": text[:1000], "summary": summary}
                result["entities"] = _extract_entities(text + "\n" + summary)
            elif ftype == "excel":
                ov = extract_excel_overview(file_path, max_rows=max_preview_rows)
                # 用LLM对结构做中文概述
                llm_summary = summarize_text(str(ov))
                result["overview"] = {"type": "excel", "structure": ov, "summary": llm_summary}
            elif ftype == "text":
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                except Exception as e:
                    result["errors"].append(f"读取文本失败: {e}")
                    text = ""
                summary = summarize_text(text)
                result["overview"] = {"type": "text", "text_excerpt": text[:1000], "summary": summary}
                result["entities"] = _extract_entities(text + "\n" + summary)
            else:
                result["errors"].append("不支持的或未知的文件类型")
        except Exception as exc:
            logger.error("文件分析失败(%s): %s", file_path, exc)
            result["errors"].append(str(exc))

        return result

    def generate_markdown(self, analysis: Dict[str, Any]) -> str:
        """根据分析结果生成中文Markdown报告。

        Args:
            analysis: `analyze` 的结构化输出。

        Returns:
            str: Markdown 文本，包含文件概览、抽取实体与建议。
        """

        llm = LLMClient()
        system = (
            "你是资深数据文档分析师，请基于提供的结构化分析结果，输出中文Markdown报告，"
            "包含：文件类型与基本信息、摘要/结构概览、检出的URL/Email/日期、潜在质量问题与误差分析、后续处理建议。"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": str(analysis)},
        ]
        return llm.chat(messages)


def _extract_entities(text: str) -> Dict[str, List[str]]:
    """简单实体抽取：URL、Email、日期。

    Args:
        text: 输入文本。

    Returns:
        Dict[str, List[str]]: 包含 `urls`、`emails`、`dates`。
    """

    urls = list(set(URL_RE.findall(text or "")))
    emails = list(set(EMAIL_RE.findall(text or "")))
    dates = list(set(DATE_RE.findall(text or "")))
    return {"urls": urls, "emails": emails, "dates": dates}