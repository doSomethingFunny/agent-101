"""配置模块。

负责读取环境变量与默认配置，用于 LLM、嵌入模型、向量库等组件。

Attributes:
    Settings: Pydantic BaseSettings 子类，提供强类型配置加载。

Raises:
    ValueError: 当必要配置缺失或非法时抛出。
"""

from __future__ import annotations

from pydantic import BaseSettings, Field, ValidationError


class Settings(BaseSettings):
    """项目运行配置。

    使用环境变量覆盖默认值，所有字段均具备类型校验与合理默认。

    Attributes:
        openai_api_key: OpenAI API Key，用于模型与嵌入服务。
        chat_model: Chat 对话模型名称，例如 `gpt-4o-mini`。
        embedding_model: Embedding 模型名称，例如 `text-embedding-3-small`。
        request_timeout_seconds: 外部请求超时时间（秒）。
        chroma_persist_dir: Chroma 向量库持久化目录。
        max_context_tokens: 短期记忆的最大上下文 token 预算。
    """

    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    chat_model: str = Field(default="gpt-4o-mini", env="CHAT_MODEL")
    embedding_model: str = Field(
        default="text-embedding-3-small", env="EMBEDDING_MODEL"
    )
    request_timeout_seconds: int = Field(default=25, env="REQUEST_TIMEOUT_SECONDS")
    chroma_persist_dir: str = Field(default=".chroma", env="CHROMA_PERSIST_DIR")
    max_context_tokens: int = Field(default=4000, env="MAX_CONTEXT_TOKENS")
    semantic_scholar_api_key: str = Field(default="", env="SEMANTIC_SCHOLAR_API_KEY")


def load_settings() -> Settings:
    """加载项目配置。

    Returns:
        Settings: 已加载并校验的配置对象。

    Raises:
        ValueError: 当配置校验失败或缺少必要环境变量时。
    """

    try:
        settings = Settings()
    except ValidationError as exc:  # pragma: no cover - 简单配置校验
        raise ValueError(f"配置加载失败: {exc}") from exc

    return settings