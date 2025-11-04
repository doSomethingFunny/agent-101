"""Planner+Executor 演示脚本（Week 2）。

运行 LangGraph 应用：先规划步骤，再在执行循环中进行工具选择与调用，最终汇总答案。

Usage:
    python scripts/demo_planner_executor.py --question "抓取某URL并做简单计算，再搜索相关资料"
"""

from __future__ import annotations

import argparse
from typing import Optional

from src.agent101.executor.langgraph_app import PlannerExecutorApp
from src.agent101.logger import get_logger


logger = get_logger("demo-week2")


def main(question: Optional[str] = None) -> None:
    parser = argparse.ArgumentParser(description="Agent 101 Week2 Planner+Executor 演示")
    parser.add_argument("--question", type=str, required=False, help="用户问题")
    args = parser.parse_args()

    q = question or args.question or "请规划并执行：计算(12+5)*3，抓取'https://example.com'文本，进行一次Web搜索，并最终汇总答案。"

    app = PlannerExecutorApp()
    try:
        result = app.run(q)
        print("\n=== 计划 ===\n")
        print(result.get("plan"))
        print("\n=== 工具输出 ===\n")
        print(result.get("tool_outputs"))
        print("\n=== 最终答案 ===\n")
        print(result.get("final_answer"))
        if result.get("error"):
            print("\n[错误]", result.get("error"))
    except Exception as exc:
        logger.error("运行失败: %s", exc)


if __name__ == "__main__":
    main()