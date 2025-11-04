"""运行Agent 101 API服务。

提供命令行启动方式，默认监听 0.0.0.0:8000。

Usage:
    python scripts/run_server.py --host 127.0.0.1 --port 8080
"""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent 101 FastAPI server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen")
    args = parser.parse_args()

    uvicorn.run("src.agent101.server.api:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()