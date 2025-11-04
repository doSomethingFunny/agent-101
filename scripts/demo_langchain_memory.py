"""LangChain 记忆系统演示脚本。

展示短期记忆（会话历史）在 LCEL 中的使用方法，基于 RunnableWithMessageHistory。

运行示例：
    python scripts/demo_langchain_memory.py --session u1

环境要求：
    - 设置环境变量 OPENAI_API_KEY
"""

from __future__ import annotations

import argparse
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory


store: Dict[str, InMemoryChatMessageHistory] = {}


def get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def run(session_id: str) -> str:
    llm = ChatOpenAI(temperature=0)
    chain = RunnableWithMessageHistory(
        llm,
        get_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # 第一次对话：写入偏好
    chain.invoke({"input": "你好，记住我喜欢LangChain。"}, config={"configurable": {"session_id": session_id}})
    # 第二次对话：测试记忆检索
    resp = chain.invoke({"input": "我喜欢什么？"}, config={"configurable": {"session_id": session_id}})

    assert isinstance(resp, AIMessage)
    return resp.content


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: Memory with RunnableWithMessageHistory")
    parser.add_argument("--session", type=str, default="u1", help="会话ID")
    args = parser.parse_args()

    answer = run(args.session)
    print("=== 记忆查询答案 ===")
    print(answer)


if __name__ == "__main__":
    main()