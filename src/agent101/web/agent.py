"""网页操作Agent。

执行多步骤网页任务，支持错误处理、日志记录与截图保存。

Classes:
    WebAgent: 按步骤执行网页动作并收集结果。
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..logger import get_logger
from .browser import BrowserManager
from .actions import execute_action


logger = get_logger(__name__)


class WebAgent:
    """多步骤网页操作Agent。"""

    def __init__(self, headless: bool = True) -> None:
        self.browser = BrowserManager(headless=headless)

    def run(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行步骤列表。

        Args:
            steps: 动作字典列表（参见 `actions.execute_action` 支持的类型）。

        Returns:
            Dict[str, Any]: 包含 `results`（每步输出）与 `errors`（失败信息）。
        """

        self.browser.start()
        results: List[Any] = []
        errors: List[str] = []

        try:
            for i, action in enumerate(steps):
                try:
                    out = execute_action(self.browser, action)
                    results.append({"step": i, "type": action.get("type"), "output": out})
                except Exception as exc:
                    logger.error("步骤失败(%s): %s", action.get("type"), exc)
                    errors.append(f"step {i} ({action.get('type')}): {exc}")
        finally:
            self.browser.stop()

        return {"results": results, "errors": errors}