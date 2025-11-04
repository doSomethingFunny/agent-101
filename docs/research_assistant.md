# 智能科研助理（Week 3）

## 概述
- 功能：学术检索（arXiv/Semantic Scholar）、PDF解析与分块摘要、结构化中文综述生成（Markdown）。
- 目标：自动化生成主题相关的综述报告，支持多个PDF输入并融合结果。

## 模块
- `src/agent101/research/academic_search.py`：检索封装。
- `src/agent101/research/pdf_parser.py`：PDF文本提取、分块与摘要。
- `src/agent101/research/review_generator.py`：融合生成Markdown综述。

## 依赖与配置
- 依赖：`arxiv`, `semanticscholar`, `pypdf`。
- 可选配置：`SEMANTIC_SCHOLAR_API_KEY`（提升速率与配额）。

## 运行示例
```bash
python scripts/demo_research_assistant.py --topic "Graph RAG" --pdf .\samples\paper1.pdf --pdf .\samples\paper2.pdf
```

## 设计与工程化
- 错误处理：检索与PDF解析失败不会中断流程；日志记录失败项。
- 性能优化：PDF分块摘要并二次汇总；检索结果数量可控；LLM统一超时。
- 输出结构：综述Markdown包含引言、关键进展、方法比较、应用与局限、结论、参考链接。

## 扩展建议
- 综述模板：可加入固定章节模板与引用格式（BibTeX）。
- 质量评估：对摘要与综述输出进行一致性检测或关键点覆盖率评估。
- 与长期记忆结合：将摘要与检索结果写入向量库用于后续任务。