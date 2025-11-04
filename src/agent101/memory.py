"""记忆模块。

提供短期记忆（上下文消息管理与截断）与长期记忆（向量检索）。

Classes:
    ShortTermMemory: 管理对话上下文与 token 预算。
    VectorMemory: 抽象类，定义写入与查询接口。
    ChromaVectorMemory: 基于 Chroma 的长期记忆实现。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import tiktoken
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from .config import load_settings
from .logger import get_logger


logger = get_logger(__name__)


class ShortTermMemory:
    """短期记忆管理。

    通过 token 预算控制上下文长度，避免超过模型窗口导致成本与延迟增加。

    Args:
        max_tokens: 最大上下文 token 预算。
        model: 用于估算的模型名称（与聊天模型一致更准确）。

    Attributes:
        messages: 当前已记录的聊天消息列表（role/content）。
    """

    def __init__(self, max_tokens: Optional[int] = None, model: Optional[str] = None) -> None:
        settings = load_settings()
        self.max_tokens = max_tokens or settings.max_context_tokens
        self.model = model or settings.chat_model
        self.messages: List[Dict[str, Any]] = []

    def add(self, role: str, content: str) -> None:
        """添加消息并在必要时进行截断。

        Args:
            role: `system`/`user`/`assistant`。
            content: 文本内容。
        """

        self.messages.append({"role": role, "content": content})
        self._truncate_if_needed()

    def get(self) -> List[Dict[str, Any]]:
        """获取当前消息列表。"""

        return list(self.messages)

    def _truncate_if_needed(self) -> None:
        """基于 token 预算进行上下文截断。"""

        try:
            enc = tiktoken.encoding_for_model(self.model)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")

        def tokens_of_messages(msgs: Sequence[Dict[str, Any]]) -> int:
            text = "\n".join(str(m.get("content", "")) for m in msgs)
            return len(enc.encode(text))

        while self.messages and tokens_of_messages(self.messages) > self.max_tokens:
            # 丢弃最早的一条消息以控制窗口
            dropped = self.messages.pop(0)
            logger.debug("短期记忆截断，移除: %s", dropped)


class VectorMemory:
    """长期记忆抽象。

    定义写入与查询接口，具体实现可基于 Chroma/FAISS 等向量库。
    """

    def add(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """写入文本及其元信息。

        Args:
            texts: 待向量化的文本集合。
            metadatas: 对应的元信息列表，可为 None。
        """

        raise NotImplementedError

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """向量检索相似文本。

        Args:
            query: 查询文本。
            k: 返回条目数量。

        Returns:
            List[Dict[str, Any]]: 包含文本与元数据的检索结果。
        """

        raise NotImplementedError


class ChromaVectorMemory(VectorMemory):
    """基于 Chroma 的长期记忆实现。"""

    def __init__(self, persist_dir: Optional[str] = None) -> None:
        settings = load_settings()
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.embeddings = OpenAIEmbeddings(model=settings.embedding_model)
        self.vs = Chroma(
            collection_name="agent101_memory",
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir,
        )

    def add(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        try:
            self.vs.add_texts(texts=texts, metadatas=metadatas)
            self.vs.persist()
        except Exception as exc:  # pragma: no cover
            logger.error("Chroma 写入失败: %s", exc)

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        try:
            docs = self.vs.similarity_search(query, k=k)
        except Exception as exc:  # pragma: no cover
            logger.error("Chroma 检索失败: %s", exc)
            return []

        results: List[Dict[str, Any]] = []
        for d in docs:
            results.append({"text": d.page_content, "metadata": d.metadata})
        return results