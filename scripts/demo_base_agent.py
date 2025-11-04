"""基础 Agent 演示脚本。

运行一个最小示例：使用函数调用执行计算与搜索，并返回综合答案。

Usage:
    python scripts/demo_base_agent.py --question "(12+5)*3 的值是多少？并搜索相关背景"
"""

from __future__ import annotations

import argparse
from typing import Optional

from src.agent101.agents.base_qa import BaseQAAgent
from src.agent101.logger import get_logger


logger = get_logger("demo")


def main(question: Optional[str] = None) -> None:
    parser = argparse.ArgumentParser(description="Agent 101 基础Agent演示")
    parser.add_argument("--question", type=str, required=False, help="用户问题")
    args = parser.parse_args()

    q = question or args.question or "请先进行一次计算 1+2*3，并进行一次简单的Web搜索";
    agent = BaseQAAgent(enable_vector_memory=True)
    try:
        answer = agent.ask(q)
        print("\n=== 最终答案 ===\n")
        print(answer)
    except Exception as exc:
        logger.error("运行失败: %s", exc)


if __name__ == "__main__":
    main()