# 项目技术概览

本项目以模块化的方式构建可扩展的 AI Agent：

- LLM 接入：OpenAI，经 LangChain 封装，支持 Function Calling。
- 记忆系统：
  - 短期记忆：对话消息管理与上下文截断（tiktoken 估算）。
  - 长期记忆：Chroma/FAISS 向量检索，OpenAI Embeddings。
- 工具系统：DuckDuckGo 搜索、计算器（AST 安全求值）。
- Agent 策略：ReAct 基本流程，后续扩展 Reflexion。
- 日志与错误处理：统一 logging，超时与重试，异常语义化。
- 性能优化：请求超时、最小上下文、工具结果压缩，目标 <3s。

## 设计原则
- 高内聚、低耦合：模块独立测试。
- 明确接口与文档：Google-style docstring，中文说明。
- 可扩展：便于添加新的工具、记忆与策略。