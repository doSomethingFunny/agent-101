# Week 4 网页操作 Agent

本模块提供基于 Playwright 的网页操作能力，支持启动/关闭浏览器、页面导航、元素等待、输入、点击、文本提取与截图。并通过 `WebAgent` 组合多步骤执行。

## 结构

- `src/agent101/web/browser.py`: 浏览器封装（同步）。
- `src/agent101/web/actions.py`: 标准动作库与分发。
- `src/agent101/web/agent.py`: 多步骤执行的 WebAgent。
- `scripts/demo_web_agent.py`: DuckDuckGo 搜索演示脚本。

## 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install
```

## 运行演示

```bash
python scripts/demo_web_agent.py --query "LangGraph" --headless
```

输出包含每步的结果、截图保存路径与可能的错误。截图位于 `artifacts/web` 目录。

## 设计与扩展

- 同步API以简化集成；后续可切换到异步提高并发。
- 动作与 Agent 解耦，便于扩展更多动作（滚动、上传、下载、表格抓取等）。
- 提供统一错误处理与日志，便于定位问题。