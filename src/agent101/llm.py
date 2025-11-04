"""LLM 客户端封装。

封装 OpenAI Chat/Embeddings 调用，支持 Function Calling 与超时控制。

Classes:
    LLMClient: OpenAI 客户端，提供通用聊天与函数调用会话。

Raises:
    RuntimeError: 当请求失败或返回内容为空。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import load_settings
from .logger import get_logger


logger = get_logger(__name__)


class LLMClient:
    """OpenAI LLM 客户端封装。

    Args:
        api_key: OpenAI API Key；若为空则从配置读取。
        model: Chat 模型名称；若为空则从配置读取。
        timeout_seconds: 请求超时时间；若为空则从配置读取。

    Attributes:
        client: OpenAI Python SDK 客户端实例。
        model: 当前使用的对话模型名称。
        timeout_seconds: 请求超时时间（秒）。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        settings = load_settings()
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.chat_model
        self.timeout_seconds = timeout_seconds or settings.request_timeout_seconds

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """执行普通聊天请求。

        Args:
            messages: OpenAI Chat 格式的消息列表。

        Returns:
            str: 模型返回的文本内容。

        Raises:
            RuntimeError: 当返回为空或请求异常时。
        """

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=self.timeout_seconds,
            )
        except Exception as exc:  # pragma: no cover
            logger.error("LLM chat 请求失败: %s", exc)
            raise RuntimeError("LLM chat 请求失败") from exc

        content = resp.choices[0].message.content if resp.choices else None
        if not content:
            raise RuntimeError("LLM 返回为空")
        return content

    def function_call_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """执行带 Function Calling 的聊天请求。

        Args:
            messages: OpenAI Chat 格式的消息列表。
            tools: OpenAI `tools` 规范的函数列表（JSON Schema）。

        Returns:
            Dict[str, Any]: 原始返回对象的精简字典，包含 `message` 与 `tool_calls`。

        Raises:
            RuntimeError: 当返回为空或请求异常时。
        """

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                timeout=self.timeout_seconds,
            )
        except Exception as exc:  # pragma: no cover
            logger.error("LLM function_call 请求失败: %s", exc)
            raise RuntimeError("LLM function_call 请求失败") from exc

        message = resp.choices[0].message if resp.choices else None
        if not message:
            raise RuntimeError("LLM 返回为空")

        return {
            "content": message.content,
            "tool_calls": message.tool_calls or [],
        }