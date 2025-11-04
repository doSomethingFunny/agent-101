"""简单URL抓取工具。

使用 `requests` 获取网页纯文本内容并截断返回，便于在Agent中快速引用。

Functions:
    web_fetch: 抓取URL并返回截断后的文本。

Raises:
    RuntimeError: 当请求失败或状态码不为2xx。
"""

from __future__ import annotations

import re
from typing import Dict

import requests


def _strip_html(html: str) -> str:
    # 简单去标签（非严格HTML解析）
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def web_fetch(url: str, max_chars: int = 1000) -> Dict[str, str]:
    """抓取URL文本内容。

    Args:
        url: 目标地址。
        max_chars: 返回文本的最大字符数。

    Returns:
        Dict[str, str]: 包含 `url` 与 `text` 字段。

    Raises:
        RuntimeError: 当网络请求失败或非2xx响应。
    """

    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code >= 300:
            raise RuntimeError(f"HTTP状态码: {resp.status_code}")
        text = _strip_html(resp.text)
        return {"url": url, "text": text[:max_chars]}
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"抓取失败: {exc}")