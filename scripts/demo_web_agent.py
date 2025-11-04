"""网页操作Agent演示脚本（Week 4）。

示例：在 DuckDuckGo 搜索关键词并抓取前若干条结果标题。

Usage:
    python scripts/demo_web_agent.py --query "LangChain"
"""

from __future__ import annotations

import argparse

from src.agent101.web.agent import WebAgent
from src.agent101.logger import get_logger


logger = get_logger("demo-week4")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent 101 Week4 网页操作Agent演示")
    parser.add_argument("--query", type=str, default="LangGraph", help="搜索关键词")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    args = parser.parse_args()

    steps = [
        {"type": "goto", "url": "https://duckduckgo.com"},
        {"type": "wait_for_selector", "selector": "input[name=q]"},
        {"type": "fill", "selector": "input[name=q]", "text": args.query},
        {"type": "click", "selector": "input[type=submit]"},
        {"type": "wait_for_selector", "selector": "#links"},
        {"type": "screenshot", "name": "duckduckgo_results"},
        {"type": "extract_text", "selector": "#links .result__title"},
    ]

    agent = WebAgent(headless=args.headless)
    try:
        result = agent.run(steps)
        print("\n=== 结果 ===\n")
        for r in result["results"]:
            print(r)
        if result["errors"]:
            print("\n[错误]", result["errors"])
    except Exception as exc:
        logger.error("运行失败: %s", exc)


if __name__ == "__main__":
    main()