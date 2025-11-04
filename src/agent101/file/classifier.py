"""文件类型分类器。

提供基于扩展名的快速分类，并在必要时进行简单内容嗅探。

Functions:
    classify_file_type: 返回标准化文件类型标识。
"""

from __future__ import annotations

import os
from typing import Literal


FileType = Literal["pdf", "word", "excel", "text", "unknown"]


def classify_file_type(path: str) -> FileType:
    """根据文件扩展名分类文件类型。

    Args:
        path: 文件路径。

    Returns:
        FileType: `pdf`/`word`/`excel`/`text`/`unknown`。

    Notes:
        - 该函数优先使用扩展名判断；若无扩展名则返回 `unknown`。
        - 可在后续扩展为基于MIME类型或内容嗅探。
    """

    _, ext = os.path.splitext(path.lower())
    if ext in {".pdf"}:
        return "pdf"
    if ext in {".docx"}:
        return "word"
    if ext in {".xlsx", ".xlsm", ".xls"}:
        return "excel"
    if ext in {".txt", ".md", ".markdown"}:
        return "text"
    return "unknown"