# Week 5 API 服务

提供统一的 FastAPI 服务，将前几周的能力暴露为 HTTP 接口：

- `/healthz`: 健康检查。
- `/v1/agent/plan-execute`: 运行 Planner+Executor。
- `/v1/research/review`: 学术检索 + PDF 摘要并生成中文综述 Markdown。
- `/v1/web/execute`: 执行网页操作步骤（基于 Playwright）。
- `/v1/agent/base-qa`: 基础问答Agent（可选开启向量记忆）。

## 安装与启动

```bash
pip install -r requirements.txt
python scripts/run_server.py --host 127.0.0.1 --port 8000
```

默认可访问 `http://127.0.0.1:8000/docs` 查看OpenAPI文档。

## 请求示例

- Planner+Executor

```json
POST /v1/agent/plan-execute
{
  "question": "用计算器计算(12+5)*3，并搜索LangGraph的含义"
}
```

- Research Review

```json
POST /v1/research/review
{
  "topic": "Retrieval-Augmented Generation",
  "max_results": 5,
  "pdf_paths": ["/path/to/paper.pdf"]
}
```

- Web Execute

```json
POST /v1/web/execute
{
  "headless": true,
  "steps": [
    {"type": "goto", "url": "https://duckduckgo.com"},
    {"type": "wait_for_selector", "selector": "input[name=q]"},
    {"type": "fill", "selector": "input[name=q]", "text": "LangGraph"},
    {"type": "click", "selector": "input[type=submit]"},
    {"type": "wait_for_selector", "selector": "#links"},
    {"type": "extract_text", "selector": "#links .result__title"}
  ]
}
```

- File Analyze

```json
POST /v1/file/analyze
{
  "file_path": "/path/to/file.pdf",
  "max_preview_rows": 5
}
```

- Base QA

```json
POST /v1/agent/base-qa
{
  "question": "什么是LangGraph?",
  "enable_vector_memory": true
}
```

也可以使用演示脚本调用服务：

```bash
python scripts/demo_base_agent.py --question "什么是LangGraph?" --host 127.0.0.1 --port 8000
```

## 设计说明

- 强类型 Pydantic 模型，明确参数与返回结构，便于前端集成与测试。
- 统一错误处理：服务端捕获异常并返回 `HTTP 500` 与 `detail`。
- 与现有模块解耦：API层仅组装与调用内部能力，便于演进。
- 可拓展：后续可加入认证、配额、异步执行、任务队列等。