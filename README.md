# Agent 101 — 综合性 AI Agent 学习项目

本项目旨在系统化学习与实践 AI Agent 技术栈，包含基础理论实现、核心能力模块与多个实战场景的可运行示例。采用 LangChain/LangGraph 进行模块化构建，注重工程化、可测试性与可扩展性。

## 快速开始

- Python 版本建议：`>=3.10`
- 设置环境变量：`OPENAI_API_KEY`

```bash
# Windows PowerShell（建议使用虚拟环境）
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 运行基础 Agent 演示（需有效的 OPENAI_API_KEY）
python scripts/demo_base_agent.py --question "如何计算(12+5)*3，并搜索相关背景?"
```

## 项目结构

```
agent-101/
├─ src/agent101/
│  ├─ agents/base_qa.py         # 基础问答Agent（ReAct + Function Calling）
│  ├─ tools/calculator.py       # 安全计算器工具
│  ├─ tools/web_search.py       # DuckDuckGo 搜索工具
│  ├─ memory.py                 # 短期/长期记忆模块（Chroma）
│  ├─ llm.py                    # OpenAI/LangChain 封装
│  ├─ config.py                 # 配置与环境读取
│  ├─ logger.py                 # 统一日志与错误处理
│  └─ __init__.py
├─ scripts/demo_base_agent.py   # CLI 演示脚本
├─ docs/overview.md             # 技术概览
├─ docs/milestones.md           # 里程碑计划与进度
├─ requirements.txt             # 依赖清单
└─ README.md
```

## 目标与里程碑

1. 基础理论学习与原型实现
   - ReAct/Reflexion 原理学习与最小实现
   - 记忆机制：短期（上下文窗口管理）、长期（Chroma/FAISS）

2. 核心功能开发
   - 工具系统：OpenAI Function Calling + 自定义工具（搜索/计算器）
   - 规划与任务分解：LLM Planner + 多步骤执行监控

3. 项目实战
   - 智能科研助理：PDF 解析、学术检索、文献综述生成
   - 网页操作 Agent：Playwright/Selenium 自动化
   - 文件处理 Agent：PDF/Word/Excel 分类与信息抽取，结构化报告

4. 技术实现要求
   - LangChain/LangGraph 构建；模块化可独立测试
   - 完整错误处理与日志系统；响应时间优化（<3s）

5. 学习产出物
   - 可运行代码仓库、技术文档、演示案例、性能报告

## 环境变量

- `OPENAI_API_KEY`: OpenAI Key，用于模型与嵌入服务

## 性能与工程化

- 使用标准 `logging` 记录结构化日志
- 封装重试与超时，避免阻塞
- 记忆模块支持向量检索，提高上下文复用

## 后续计划

- Planner/Executor 多步骤任务分解与监控
- 实战模块逐步充实与测试覆盖
- FastAPI 服务化与前端演示页面（可选）