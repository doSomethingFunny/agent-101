"""基础问答 Agent（ReAct + Function Calling）。

实现最小可用的工具调用循环：LLM 决策 -> 调用工具 -> 写回结果 -> 生成最终答案。

Classes:
    BaseQAAgent: 支持短期记忆与长期记忆检索的问答代理。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ..llm import LLMClient
from ..memory import ShortTermMemory, ChromaVectorMemory
from ..tools import list_tool_schemas
from ..tools import evaluate_expression, web_search
from ..logger import get_logger


logger = get_logger(__name__)


class BaseQAAgent:
    """基础问答代理。

    Args:
        enable_vector_memory: 是否启用长期记忆检索。
        max_tool_steps: 最大工具调用步数，防止死循环。

    Attributes:
        llm: LLM 客户端实例。
        stm: 短期记忆管理器。
        vmem: 长期记忆（Chroma）。
    """

    def __init__(
        self,
        enable_vector_memory: bool = True,
        max_tool_steps: int = 3,
    ) -> None:
        self.llm = LLMClient()
        self.stm = ShortTermMemory()
        self.vmem = ChromaVectorMemory() if enable_vector_memory else None
        self.max_tool_steps = max_tool_steps

    def ask(self, question: str) -> str:
        """提出问题并返回答案。

        流程：
        1) 将用户问题写入短期记忆；
        2) 可选：查询长期记忆并作为系统上下文补充；
        3) 进入工具调用循环（ReAct）；
        4) 返回最终答案并将摘要写入长期记忆。

        Args:
            question: 用户输入问题。

        Returns:
            str: Agent 返回的最终文本答案。

        Raises:
            RuntimeError: 当LLM或工具调用异常导致无法生成答案时。
        """

        system_context = "你是一个具备工具使用能力的助理，善用函数进行计算与搜索。"
        self.stm.add("system", system_context)
        self.stm.add("user", question)

        # 长期记忆检索作为辅助上下文
        if self.vmem:
            memories = self.vmem.search(question, k=3)
            if memories:
                memo_text = "\n".join([m.get("text", "") for m in memories])
                self.stm.add("system", f"相关记忆: \n{memo_text}")

        messages = self.stm.get()
        tools = list_tool_schemas()

        # 工具调用循环
        for step in range(self.max_tool_steps):
            result = self.llm.function_call_chat(messages=messages, tools=tools)
            tool_calls = result.get("tool_calls", [])
            content = result.get("content") or ""

            if tool_calls:
                # 执行所有工具调用并追加到上下文
                for tc in tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments or "{}")

                    try:
                        if name == "evaluate_expression":
                            calc_res = evaluate_expression(args.get("expression", ""))
                            messages.append(
                                {
                                    "role": "tool",
                                    "content": json.dumps(
                                        {"name": name, "result": calc_res}, ensure_ascii=False
                                    ),
                                }
                            )
                        elif name == "web_search":
                            results = web_search(
                                args.get("query", ""),
                                max_results=int(args.get("max_results", 5) or 5),
                            )
                            messages.append(
                                {
                                    "role": "tool",
                                    "content": json.dumps(
                                        {"name": name, "result": results}, ensure_ascii=False
                                    ),
                                }
                            )
                        else:
                            messages.append(
                                {
                                    "role": "tool",
                                    "content": json.dumps(
                                        {"name": name, "error": "未知工具"}, ensure_ascii=False
                                    ),
                                }
                            )
                    except Exception as exc:  # 工具异常写回上下文，避免中断
                        messages.append(
                            {
                                "role": "tool",
                                "content": json.dumps(
                                    {"name": name, "error": str(exc)}, ensure_ascii=False
                                ),
                            }
                        )

                # 工具调用后继续与模型交互以生成答案
                continue

            # 无工具调用，视为已得到最终答案
            final_answer = content.strip()
            if not final_answer:
                raise RuntimeError("LLM 未返回有效答案")

            # 写入长期记忆摘要
            if self.vmem:
                try:
                    self.vmem.add([final_answer], metadatas=[{"source": "final_answer"}])
                except Exception:
                    # 记忆写入失败不阻断流程
                    pass

            return final_answer

        # 超过最大步数仍未生成答案，尝试直接输出最后一次内容
        return result.get("content", "抱歉，未能完成任务")