"""LangChain RAG（检索增强生成）演示脚本。

构建最小 RAG 流程：加载 -> 切分 -> 嵌入 -> 入库 -> 检索 -> 生成。

运行示例：
    python scripts/demo_langchain_rag.py --question "什么是 LangChain?" --doc docs/sample.txt

环境要求：
    - 设置环境变量 OPENAI_API_KEY

依赖：
    - langchain-text-splitters（RecursiveCharacterTextSplitter）
"""

from __future__ import annotations

import argparse
from pathlib import Path

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate


def format_docs(docs):
    return "\n\n".join([f"[{getattr(d, 'metadata', {}).get('source', 'doc')}]\n{ d.page_content }" for d in docs])


def run(question: str, doc_path: str) -> str:
    path = Path(doc_path)
    if not path.exists():
        return f"[错误] 文档不存在: {path}"

    docs = TextLoader(str(path), encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    splits = splitter.split_documents(docs)

    emb = OpenAIEmbeddings()
    vs = Chroma.from_documents(splits, emb, collection_name="kb", persist_directory=".chroma")
    retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是严谨的知识问答助手，使用给定上下文回答问题，并引用来源。"),
        ("human", "问题: {question}\n上下文: {context}"),
    ])

    llm = ChatOpenAI(temperature=0)

    rag_chain = (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    resp = rag_chain.invoke(question)
    return getattr(resp, "content", str(resp))


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: LangChain RAG")
    parser.add_argument("--question", type=str, default="什么是 LangChain?", help="问题")
    parser.add_argument("--doc", type=str, default="docs/sample.txt", help="知识库文本路径")
    args = parser.parse_args()

    answer = run(args.question, args.doc)
    print("=== RAG 答案 ===")
    print(answer)


if __name__ == "__main__":
    main()