"""FastAPI 服务定义（Week 5）。

聚合Planner+Executor、Research Assistant与WebAgent为HTTP接口。

Endpoints:
    - GET /healthz: 健康检查。
    - POST /v1/agent/plan-execute: 运行Planner+Executor。
    - POST /v1/research/review: 学术检索+PDF摘要并生成综述Markdown。
    - POST /v1/web/execute: 执行多步骤网页动作。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..executor.langgraph_app import PlannerExecutorApp
from ..research.academic_search import search_arxiv, search_semantic_scholar
from ..research.pdf_parser import extract_text_from_pdf, chunk_text, summarize_chunks
from ..research.review_generator import generate_review_markdown
from ..web.agent import WebAgent
from ..file.agent import FileAgent
from ..agents.base_qa import BaseQAAgent
from ..logger import get_logger


logger = get_logger(__name__)


class PlanExecuteRequest(BaseModel):
    """Planner+Executor 请求模型。"""

    question: str = Field(..., description="用户问题或任务描述")


class ToolRunOutput(BaseModel):
    """工具执行输出记录。"""

    name: str
    args: Dict[str, Any]
    result: Any


class PlanExecuteResponse(BaseModel):
    """Planner+Executor 响应模型。"""

    final_answer: Optional[str] = None
    plan: List[Dict[str, Any]] = []
    tool_outputs: List[Dict[str, Any]] = []
    error: Optional[str] = None


class ResearchReviewRequest(BaseModel):
    """研究综述生成请求。"""

    topic: str = Field(..., description="综述主题或检索关键词")
    max_results: int = Field(5, ge=1, le=20, description="每源最大检索数量")
    pdf_paths: List[str] = Field(default_factory=list, description="本地PDF路径列表")


class ResearchReviewResponse(BaseModel):
    """研究综述响应。"""

    markdown: str
    arxiv_results: List[Dict[str, str]]
    semantic_results: List[Dict[str, str]]
    pdf_summaries: List[str]


class WebExecuteRequest(BaseModel):
    """网页动作执行请求。"""

    steps: List[Dict[str, Any]] = Field(..., description="动作步骤列表")
    headless: bool = Field(True, description="是否无头模式运行")


class WebExecuteResponse(BaseModel):
    """网页动作执行响应。"""

    results: List[Dict[str, Any]]
    errors: List[str]


class FileAnalyzeRequest(BaseModel):
    """文件分析请求模型。"""

    file_path: str = Field(..., description="待分析文件的本地路径")
    max_preview_rows: int = Field(5, ge=1, le=50, description="Excel示例行上限")


class FileAnalyzeResponse(BaseModel):
    """文件分析响应模型。"""

    file_path: str
    file_type: str
    overview: Dict[str, Any]
    entities: Dict[str, List[str]]
    errors: List[str]
    markdown: Optional[str] = None

class BaseQARequest(BaseModel):
    """基础Agent问答请求模型。

    Attributes:
        question: 用户输入的问题。
        enable_vector_memory: 是否启用长期记忆检索。
    """

    question: str = Field(..., description="用户问题")
    enable_vector_memory: bool = Field(True, description="是否启用长期记忆")


class BaseQAResponse(BaseModel):
    """基础Agent问答响应模型。"""

    answer: str

def create_app() -> FastAPI:
    """创建并返回 FastAPI 应用。

    Returns:
        FastAPI: 配置完成的应用实例。
    """

    app = FastAPI(title="Agent 101 API", version="0.5.0")

    @app.get("/healthz")
    def healthz() -> Dict[str, str]:
        """健康检查。

        Returns:
            Dict[str, str]: 固定返回 `{"status": "ok"}`。
        """

        return {"status": "ok"}

    @app.post("/v1/agent/plan-execute", response_model=PlanExecuteResponse)
    def plan_execute(req: PlanExecuteRequest) -> PlanExecuteResponse:
        """运行 Planner+Executor，并返回规划、工具输出与最终答案。

        Args:
            req: 包含 `question` 的请求。

        Returns:
            PlanExecuteResponse: 执行结果结构。
        """

        try:
            app_inst = PlannerExecutorApp()
            result = app_inst.run(req.question)
            return PlanExecuteResponse(**result)
        except Exception as exc:
            logger.error("planner-executor 失败: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/v1/research/review", response_model=ResearchReviewResponse)
    def research_review(req: ResearchReviewRequest) -> ResearchReviewResponse:
        """执行学术检索、PDF摘要并生成中文综述Markdown。"""

        try:
            arxiv_res = search_arxiv(req.topic, max_results=req.max_results)
            semantic_res = search_semantic_scholar(req.topic, max_results=req.max_results)

            pdf_summaries: List[str] = []
            for path in req.pdf_paths:
                try:
                    text = extract_text_from_pdf(path)
                    chunks = chunk_text(text, max_chars=3000)
                    summary = summarize_chunks(chunks)
                    pdf_summaries.append(summary)
                except Exception as e:
                    logger.warning("PDF处理失败(%s): %s", path, e)
                    pdf_summaries.append(f"[错误] 无法解析或摘要: {path}")

            md = generate_review_markdown(
                topic=req.topic,
                arxiv_results=arxiv_res,
                semantic_results=semantic_res,
                pdf_summaries=pdf_summaries,
            )

            return ResearchReviewResponse(
                markdown=md,
                arxiv_results=arxiv_res,
                semantic_results=semantic_res,
                pdf_summaries=pdf_summaries,
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("research-review 失败: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/v1/web/execute", response_model=WebExecuteResponse)
    def web_execute(req: WebExecuteRequest) -> WebExecuteResponse:
        """执行网页动作步骤。

        Args:
            req: 包含步骤与运行模式的请求。

        Returns:
            WebExecuteResponse: 每步输出与错误列表。
        """

        try:
            agent = WebAgent(headless=req.headless)
            res = agent.run(req.steps)
            return WebExecuteResponse(**res)
        except Exception as exc:
            logger.error("web-execute 失败: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/v1/agent/base-qa", response_model=BaseQAResponse)
    def base_qa(req: BaseQARequest) -> BaseQAResponse:
        """运行基础问答Agent并返回答案。"""

        try:
            agent = BaseQAAgent(enable_vector_memory=req.enable_vector_memory)
            ans = agent.ask(req.question)
            return BaseQAResponse(answer=ans)
        except Exception as exc:
            logger.error("base-qa 失败: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/v1/file/analyze", response_model=FileAnalyzeResponse)
    def file_analyze(req: FileAnalyzeRequest) -> FileAnalyzeResponse:
        """分析本地文件并返回结构化结果与Markdown报告。"""

        try:
            agent = FileAgent()
            analysis = agent.analyze(req.file_path, max_preview_rows=req.max_preview_rows)
            # 始终生成Markdown，便于前端展示
            md = agent.generate_markdown(analysis)
            analysis["markdown"] = md
            return FileAnalyzeResponse(**analysis)
        except Exception as exc:
            logger.error("file-analyze 失败: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    return app


# 便于 Uvicorn 直接加载： `uvicorn src.agent101.server.api:app`
app = create_app()