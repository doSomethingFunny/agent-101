"""统一日志模块。

提供结构化日志记录与便捷获取，所有模块应使用此处的 logger。

Functions:
    get_logger: 返回按模块名配置的 logger。
"""

import logging
from typing import Optional


def _configure_root_logger() -> None:
    """配置根日志器。

    使用标准 `logging`，输出包含时间、等级、模块与消息，便于调试与排错。
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


_configure_root_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取模块 logger。

    Args:
        name: 模块或组件名称；为 None 时返回根 logger。

    Returns:
        logging.Logger: 可直接用于记录信息、警告与错误。
    """

    return logging.getLogger(name)