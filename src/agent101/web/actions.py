"""网页操作动作库。

定义可执行的标准动作并提供分发函数，便于在 WebAgent 中进行多步骤自动化。

Functions:
    execute_action: 执行单个动作并返回结果或空字符串。
"""

from __future__ import annotations

from typing import Dict, Any

from .browser import BrowserManager


def execute_action(browser: BrowserManager, action: Dict[str, Any]) -> str:
    """执行一个网页动作。

    支持的动作：
    - goto: {url}
    - wait_for_selector: {selector}
    - fill: {selector, text}
    - click: {selector}
    - extract_text: {selector}
    - screenshot: {name}

    Args:
        browser: 浏览器管理器。
        action: 动作字典。

    Returns:
        str: 结果文本（如提取的文本或空字符串）。

    Raises:
        ValueError: 当动作类型未知或参数缺失时。
    """

    t = action.get("type")
    if t == "goto":
        url = action.get("url")
        if not url:
            raise ValueError("goto 需要 url")
        browser.goto(url)
        return ""
    elif t == "wait_for_selector":
        sel = action.get("selector")
        if not sel:
            raise ValueError("wait_for_selector 需要 selector")
        browser.wait_for_selector(sel)
        return ""
    elif t == "fill":
        sel = action.get("selector")
        text = action.get("text", "")
        if not sel:
            raise ValueError("fill 需要 selector")
        browser.fill(sel, text)
        return ""
    elif t == "click":
        sel = action.get("selector")
        if not sel:
            raise ValueError("click 需要 selector")
        browser.click(sel)
        return ""
    elif t == "extract_text":
        sel = action.get("selector")
        if not sel:
            raise ValueError("extract_text 需要 selector")
        return browser.extract_text(sel)
    elif t == "screenshot":
        name = action.get("name", "page")
        path = browser.screenshot(name)
        return path
    else:
        raise ValueError(f"未知动作类型: {t}")