# Agent 101 — 综合性 AI Agent 学习项目

本项目旨在系统化学习与实践 AI Agent 技术栈，包含基础理论实现、核心能力模块与多个实战场景的可运行示例。采用 LangChain/LangGraph 进行模块化构建，注重工程化、可测试性与可扩展性。

## 学习目标
## 项目骨架与基础Agent
- 搭建项目结构与依赖管理。
- 实现基础 ReAct 问答 Agent（含 Function Calling）。
- 接入短期/长期记忆（Chroma）。
- 完成 CLI 演示与基础文档。

## 工具与Planner
- 扩展工具库：文件处理、更多检索接口。
- 构建 LLM Planner 模块，支持任务分解与执行监控。
- 引入 LangGraph，定义State与Edges。

## 实战：智能科研助理
- PDF 解析与摘要生成。
- 学术数据库接口（arXiv/semantic scholar 等）。
- 文献综述报告自动生成。

## 实战：网页操作Agent
- Playwright/Selenium 浏览器控制。
- 页面元素识别与多步骤任务自动化。
- 稳定性与重试策略优化。

## 实战：文件处理Agent
- 支持 PDF/Word/Excel 分类与信息抽取。
- 结构化报告生成（JSON/Markdown）。
- 评估与误差分析。