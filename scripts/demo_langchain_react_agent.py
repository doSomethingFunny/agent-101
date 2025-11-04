"""LangChain ReAct Agent 最小演示脚本。

本脚本展示如何使用 LangChain 原生 Agent（ReAct）结合工具执行“思-行-观”循环。

运行示例：
    python scripts/demo_langchain_react_agent.py --question "搜索LangChain并计算(12+5)*3"

环境要求：
    - 设置环境变量 OPENAI_API_KEY

异常处理：
    - 对外部调用失败进行捕获并打印错误信息。
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List

from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """示例搜索工具（演示用，返回固定结果）。

    Args:
        query: 搜索关键词。
        max_results: 返回结果数量上限。

    Returns:
        List[Dict[str, str]]: 每项包含 `title` 与 `link` 字段。
    """

    return [{"title": f"{query} - 示例结果", "link": "https://example.com"}][:max_results]


def evaluate_expression(expression: str) -> str:
    """示例计算器工具（演示用，返回固定值）。

    Args:
        expression: 需要评估的表达式字符串。

    Returns:
        str: 评估结果（演示用固定返回）。
    """

    return "42"


def run(question: str) -> str:
    """运行一个最小 ReAct Agent 并返回最终答案。

    Args:
        question: 用户输入的问题。

    Returns:
        str: Agent 的最终输出文本。
    """

    tools = [
        Tool(name="web_search", func=web_search, description="执行Web搜索，返回标题与链接"),
        Tool(name="evaluate_expression", func=evaluate_expression, description="安全计算表达式"),
    ]

    llm = ChatOpenAI(temperature=0)
    prompt = (
        "你是一个善于规划与工具使用的智能体。\n"
        "当需要查询信息时调用 web_search；当需要计算时调用 evaluate_expression。\n"
        "请给出清晰的推理与最终答案。"
    )

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    try:
        result = executor.invoke({"input": question})
        return str(result.get("output", ""))
    except Exception as exc:
        return f"[错误] 执行失败: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: LangChain ReAct Agent")
    parser.add_argument("--question", type=str, required=True, help="要提问的内容")
    args = parser.parse_args()

    answer = run(args.question)
    print("=== 最终答案 ===")
    print(answer)


if __name__ == "__main__":
    main()