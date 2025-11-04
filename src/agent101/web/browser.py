"""Playwright 浏览器封装。

提供同步API以启动/关闭浏览器、创建页面、常用操作与截图保存。

Classes:
    BrowserManager: 管理浏览器生命周期与基础页面操作。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, Page

from ..logger import get_logger


logger = get_logger(__name__)


class BrowserManager:
    """Playwright 浏览器管理器（同步）。

    Args:
        headless: 是否无头模式。
        screenshots_dir: 截图保存目录，默认 `artifacts/web`。

    Attributes:
        browser: Playwright `Browser` 实例。
        page: 当前活动 `Page` 实例。
        context: 内部使用的 Playwright 上下文管理器。
    """

    def __init__(self, headless: bool = True, screenshots_dir: Optional[str] = None) -> None:
        self._pw = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.headless = headless
        self.screenshots_dir = Path(screenshots_dir or "artifacts/web")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def start(self) -> None:
        """启动浏览器并创建默认页面。"""
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=self.headless)
        context = self.browser.new_context()
        self.page = context.new_page()
        logger.info("浏览器已启动(headless=%s)", self.headless)

    def stop(self) -> None:
        """关闭页面与浏览器。"""
        try:
            if self.browser:
                self.browser.close()
        finally:
            if self._pw:
                self._pw.stop()
        logger.info("浏览器已关闭")

    def goto(self, url: str, wait_until: str = "load", timeout_ms: int = 15000) -> None:
        """打开指定URL并等待页面加载。"""
        assert self.page is not None, "浏览器未启动"
        self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)

    def click(self, selector: str, timeout_ms: int = 15000) -> None:
        """点击元素。支持CSS或文本定位（如 'text=登录'）。"""
        assert self.page is not None, "浏览器未启动"
        self.page.click(selector, timeout=timeout_ms)

    def fill(self, selector: str, text: str, timeout_ms: int = 15000) -> None:
        """在输入框填入文本。"""
        assert self.page is not None, "浏览器未启动"
        self.page.fill(selector, text, timeout=timeout_ms)

    def wait_for_selector(self, selector: str, timeout_ms: int = 15000) -> None:
        """等待元素出现。"""
        assert self.page is not None, "浏览器未启动"
        self.page.wait_for_selector(selector, timeout=timeout_ms)

    def extract_text(self, selector: str) -> str:
        """提取元素文本；如选择多个元素，将拼接返回。"""
        assert self.page is not None, "浏览器未启动"
        elements = self.page.query_selector_all(selector)
        texts = [e.inner_text() for e in elements]
        return "\n".join(texts).strip()

    def screenshot(self, name: str) -> str:
        """保存页面截图并返回文件路径。"""
        assert self.page is not None, "浏览器未启动"
        file_path = self.screenshots_dir / f"{name}.png"
        self.page.screenshot(path=str(file_path), full_page=True)
        return str(file_path)