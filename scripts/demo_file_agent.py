"""文件处理Agent演示脚本（Week 5）。

示例：输入文件路径，输出结构化分析与Markdown报告片段。

Usage:
    python scripts/demo_file_agent.py --path "./sample.xlsx"
"""

from __future__ import annotations

import argparse

from src.agent101.file.agent import FileAgent
from src.agent101.logger import get_logger


logger = get_logger("demo-week5")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent 101 Week5 文件处理Agent演示")
    parser.add_argument("--path", type=str, required=True, help="文件路径")
    parser.add_argument("--rows", type=int, default=5, help="Excel示例行上限")
    args = parser.parse_args()

    agent = FileAgent()
    try:
        res = agent.analyze(args.path, max_preview_rows=args.rows)
        md = agent.generate_markdown(res)
        print("=== 分析结果(概要) ===")
        print({k: res[k] for k in ["file_type", "entities"]})
        print("\n=== Markdown(前500字) ===\n")
        print(md[:500])
    except Exception as exc:
        logger.error("运行失败: %s", exc)


if __name__ == "__main__":
    main()