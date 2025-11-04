# Planner + Executor 技术说明（Week 2）

## 概述
- 使用 `Planner` 生成结构化步骤计划（JSON数组）。
- 使用 `LangGraph` 组织执行循环：选择工具 → 执行工具 → 记录结果 → 判断是否完成。
- 通过 `LLMClient.function_call_chat` 自动选择工具（calculator/web_search/web_fetch）。

## 模块与文件
- `src/agent101/planner/planner.py`: LLM Planner，输出 `[{goal, action}, ...]`。
- `src/agent101/executor/langgraph_app.py`: `PlannerExecutorApp`，封装LangGraph图与 `run()`。
- `src/agent101/tools/web_fetch.py`: URL抓取工具，返回截断后的纯文本。
- `src/agent101/tools/__init__.py`: 工具Schema聚合，注册 `web_fetch`。
- `scripts/demo_planner_executor.py`: CLI演示。

## 运行演示
```bash
python scripts/demo_planner_executor.py --question "计算(12+5)*3, 抓取'https://example.com', 搜索相关资料并汇总"
```

## 设计要点
- 状态结构 `AgentState` 包含 `plan/step_index/messages/tool_outputs` 等，便于监控与调试。
- 错误处理：Planner/选择/执行节点均有异常捕获，错误将写入 `error` 并结束。
- 性能优化：
  - 工具输出做截断（web_fetch `max_chars`）。
  - 控制步骤数量（Planner提示为 3-5）。
  - LLM 超时在 `LLMClient` 中统一控制。

## 扩展建议
- 步骤完成判定：为每个步骤定义显式的成功条件（如正则/指标）。
- 记忆融合：将 `tool_outputs` 中关键内容写入长期记忆，辅助后续任务。
- 更复杂的路由：依据步骤类型选择不同执行子图（例如“网页操作”子图）。