# Week 5 文件处理 Agent

支持对 PDF/Word/Excel/Text 文件进行分类、内容抽取与结构化报告生成；同时提供 FastAPI 端点供服务化调用。

## 模块结构

- `src/agent101/file/classifier.py`: 基于扩展名的快速文件类型分类。
- `src/agent101/file/extractors.py`: 抽取器集合（PDF/Word/Excel）与通用摘要函数。
- `src/agent101/file/agent.py`: 文件处理Agent，统一分析入口与Markdown生成。
- `scripts/demo_file_agent.py`: 演示脚本，输出结构化结果与Markdown片段。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 演示脚本

```bash
python scripts/demo_file_agent.py --path "./sample.xlsx" --rows 5
```

输出包含：文件类型、抽取的实体（URL/Email/日期）、以及中文Markdown报告片段。

## FastAPI 端点

- `POST /v1/file/analyze`

请求：

```json
{
  "file_path": "C:/path/to/file.xlsx",
  "max_preview_rows": 5
}
```

响应（示例缩略）：

```json
{
  "file_path": "...",
  "file_type": "excel",
  "overview": {
    "type": "excel",
    "structure": { "sheets": [ {"name": "Sheet1", "headers": ["A","B"], "rows": [[1,2],[3,4]] } ] },
    "summary": "中文概述..."
  },
  "entities": { "urls": [], "emails": [], "dates": [] },
  "errors": [],
  "markdown": "中文Markdown报告..."
}
```

## 评估与误差分析

- 抽取覆盖度：Excel 示例行与表头能否正确读取；Word/PDF 解析是否成功，摘要是否完整。
- 基本实体抽取：使用正则检测 URL/Email/日期，便于后续校对与归档。
- 错误处理：读取/解析异常会记录到 `errors` 字段，服务端返回 500 时包含 `detail` 描述。

## 扩展建议

- 更丰富的实体抽取与结构化解析（地址、金额、表格识别等）。
- 支持上传文件的多部分表单端点（`UploadFile`），便于前端页面集成。
- 增加质量评估指标与报告（如摘要一致性、字段缺失率等）。