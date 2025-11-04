"""LLM Planner 模块。

根据用户问题生成结构化的任务分解计划（步骤列表），用于后续执行与监控。

Classes:
    Planner: 使用 LLM 生成可执行的步骤计划。
"""

from __future__ import annotations

import json
from typing import List, Dict, Any

from ..llm import LLMClient


class Planner:
    """基于 LLM 的任务规划器。

    使用 Chat 接口生成结构化步骤计划，尽量输出 JSON 以便解析。

    Methods:
        plan: 输入问题，返回步骤列表（每步含目标与动作）。
    """

    def __init__(self) -> None:
        self.llm = LLMClient()

    def plan(self, question: str) -> List[Dict[str, Any]]:
        """生成任务计划。

        Args:
            question: 用户提出的问题或任务。

        Returns:
            List[Dict[str, Any]]: 步骤列表，每步建议包含 `goal` 与 `action` 字段。

        Raises:
            RuntimeError: 当 LLM 返回不可解析的结果。
        """

        system_msg = (
            "你是一个善于分解任务的Planner。将用户任务分解为3-5个可执行步骤，"
            "优先使用已有工具（calculator、web_search、web_fetch），并输出严格的JSON数组，"
            "每个元素包含: goal(目标), action(动作描述)。不要输出除JSON以外的内容。"
        )
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question},
        ]

        text = self.llm.chat(messages)
        try:
            plan = json.loads(text)
            if not isinstance(plan, list):
                raise ValueError("非数组结构")
            return plan
        except Exception as exc:
            raise RuntimeError(f"Planner 输出不可解析: {exc}\n原始: {text}")