"""LangChain MCP（多链并行）演示脚本。

展示使用 RunnableParallel 并发执行独立的可运行链，提升吞吐与响应速度。

运行示例：
    python scripts/demo_langchain_mcp.py --topic "LangChain"
"""

from __future__ import annotations

import argparse
from langchain_core.runnables import RunnableLambda, RunnableParallel


def search_news(topic: str):
    return [f"{topic}-news-1", f"{topic}-news-2"]


def search_papers(topic: str):
    return [f"{topic}-paper-1", f"{topic}-paper-2"]


def run(topic: str):
    parallel = RunnableParallel(
        news=RunnableLambda(lambda x: search_news(x["topic"])),
        papers=RunnableLambda(lambda x: search_papers(x["topic"])),
    ).with_config({"max_concurrency": 4})

    return parallel.invoke({"topic": topic})


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: MCP Multi-Chain Parallel")
    parser.add_argument("--topic", type=str, default="LangChain", help="主题词")
    args = parser.parse_args()

    result = run(args.topic)
    print("=== 并行结果 ===")
    print(result)


if __name__ == "__main__":
    main()