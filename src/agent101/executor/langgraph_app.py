"""LangGraph 执行与监控应用。

将 Planner 输出的步骤通过 LangGraph 组织为执行循环：
选择工具 → 执行工具 → 记录结果 → 判断是否完成。

Classes:
    PlannerExecutorApp: 封装 LangGraph 图并提供 run 接口。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, TypedDict, Optional

from langgraph.graph import StateGraph, END

from ..planner.planner import Planner
from ..llm import LLMClient
from ..tools import list_tool_schemas, evaluate_expression, web_search, web_fetch
from ..logger import get_logger


logger = get_logger(__name__)


class AgentState(TypedDict, total=False):
    """图状态结构。

    Attributes:
        question: 用户问题。
        plan: 步骤列表。
        step_index: 当前步骤索引。
        tool_outputs: 历次工具输出日志。
        final_answer: 最终答案。
        completed: 是否完成。
        error: 错误消息（如有）。
        messages: 与LLM交互的消息上下文。
        pending_tool_calls: 等待执行的工具调用列表（来自 LLM）。
    """

    question: str
    plan: List[Dict[str, Any]]
    step_index: int
    tool_outputs: List[Dict[str, Any]]
    final_answer: Optional[str]
    completed: bool
    error: Optional[str]
    messages: List[Dict[str, Any]]
    pending_tool_calls: List[Dict[str, Any]]


class PlannerExecutorApp:
    """Planner+Executor 的 LangGraph 应用封装。"""

    def __init__(self) -> None:
        self.planner = Planner()
        self.llm = LLMClient()
        self.tools = list_tool_schemas()
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("plan", self._node_plan)
        graph.add_node("choose", self._node_choose)
        graph.add_node("execute", self._node_execute)

        graph.add_edge("plan", "choose")
        graph.add_conditional_edges(
            "choose",
            self._route_from_choose,
            {"execute": "execute", "end": END},
        )
        graph.add_edge("execute", "choose")

        return graph.compile()

    # Nodes
    def _node_plan(self, state: AgentState) -> AgentState:
        question = state["question"]
        try:
            plan = self.planner.plan(question)
        except Exception as exc:
            return {**state, "error": f"规划失败: {exc}", "completed": True}

        messages = [
            {
                "role": "system",
                "content": "你是一个执行器。按计划逐步完成任务，必要时调用工具。",
            },
            {"role": "user", "content": question},
            {
                "role": "system",
                "content": f"当前计划: {json.dumps(plan, ensure_ascii=False)}",
            },
        ]
        return {
            **state,
            "plan": plan,
            "step_index": 0,
            "messages": messages,
            "tool_outputs": [],
        }

    def _node_choose(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        step_index = state["step_index"]
        plan = state["plan"]

        # 若计划已耗尽，生成最终答案
        if step_index >= len(plan):
            try:
                resp = self.llm.chat(messages + [{"role": "user", "content": "汇总前述信息，给出最终答案。"}])
            except Exception as exc:
                return {**state, "error": f"汇总失败: {exc}", "completed": True}
            return {**state, "final_answer": resp, "completed": True}

        current = plan[step_index]
        messages.append({"role": "system", "content": f"当前步骤: {json.dumps(current, ensure_ascii=False)}"})

        try:
            resp = self.llm.function_call_chat(messages=messages, tools=self.tools)
        except Exception as exc:
            return {**state, "error": f"选择工具失败: {exc}", "completed": True}

        tool_calls = resp.get("tool_calls", [])
        content = resp.get("content") or ""

        if tool_calls:
            # 留待执行节点处理
            return {**state, "pending_tool_calls": tool_calls}

        # 无工具调用则可能已生成中间或最终文本
        messages.append({"role": "assistant", "content": content})
        return {**state, "messages": messages, "step_index": step_index + 1}

    def _node_execute(self, state: AgentState) -> AgentState:
        calls = state.get("pending_tool_calls", [])
        messages = state["messages"]
        tool_outputs = state["tool_outputs"]

        for tc in calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            try:
                if name == "evaluate_expression":
                    result = evaluate_expression(args.get("expression", ""))
                elif name == "web_search":
                    result = web_search(args.get("query", ""), max_results=int(args.get("max_results", 5) or 5))
                elif name == "web_fetch":
                    result = web_fetch(args.get("url", ""), max_chars=int(args.get("max_chars", 1000) or 1000))
                else:
                    result = {"error": f"未知工具: {name}"}
            except Exception as exc:
                result = {"error": str(exc)}

            messages.append({"role": "tool", "content": json.dumps({"name": name, "result": result}, ensure_ascii=False)})
            tool_outputs.append({"name": name, "result": result})

        # 清空待执行调用
        state = {**state, "messages": messages, "tool_outputs": tool_outputs, "pending_tool_calls": []}
        return state

    # Routing
    def _route_from_choose(self, state: AgentState) -> str:
        if state.get("completed"):
            return "end"
        pending = state.get("pending_tool_calls", [])
        if pending:
            return "execute"
        return "execute" if state["step_index"] < len(state["plan"]) else "end"

    # Public API
    def run(self, question: str) -> Dict[str, Any]:
        """运行 Planner+Executor 图。

        Args:
            question: 用户问题。

        Returns:
            Dict[str, Any]: 包含 `final_answer`、`plan`、`tool_outputs` 与状态的结果。
        """

        initial: AgentState = {
            "question": question,
            "plan": [],
            "step_index": 0,
            "tool_outputs": [],
            "final_answer": None,
            "completed": False,
            "error": None,
            "messages": [],
            "pending_tool_calls": [],
        }

        result_state = self.graph.invoke(initial)
        return {
            "final_answer": result_state.get("final_answer"),
            "plan": result_state.get("plan", []),
            "tool_outputs": result_state.get("tool_outputs", []),
            "error": result_state.get("error"),
        }