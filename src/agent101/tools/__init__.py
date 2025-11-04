"""工具系统入口。

聚合通用工具（计算器、Web 搜索），并提供 OpenAI Function Calling 的 JSON Schema 定义。
"""

from __future__ import annotations

from typing import Dict, Any, List

from .calculator import evaluate_expression
from .web_search import web_search
from .web_fetch import web_fetch


def list_tool_schemas() -> List[Dict[str, Any]]:
    """返回用于 OpenAI Function Calling 的工具 schema 列表。

    Returns:
        List[Dict[str, Any]]: 工具 JSON Schema 列表。
    """

    return [
        {
            "type": "function",
            "function": {
                "name": "evaluate_expression",
                "description": "安全计算器：计算四则运算表达式，支持括号与浮点数。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "数学表达式，如 '(12 + 5) * 3'",
                        }
                    },
                    "required": ["expression"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "DuckDuckGo 简易搜索，返回前若干条结果的标题与链接。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "返回结果数量（默认 5）",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "web_fetch",
                "description": "抓取URL并返回截断后的纯文本内容。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "目标地址"},
                        "max_chars": {"type": "integer", "description": "最大字符数，默认1000"},
                    },
                    "required": ["url"],
                },
            },
        },
    ]


__all__ = ["evaluate_expression", "web_search", "web_fetch", "list_tool_schemas"]