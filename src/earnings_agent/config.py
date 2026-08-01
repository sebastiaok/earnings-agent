"""공통 설정: finance-mcp 연결과 도구 허용 목록.

FINANCE_MCP_DIR 환경변수로 finance-mcp 경로 지정 (기본: ../finance-mcp).
"""

from __future__ import annotations

import os
from pathlib import Path

FINANCE_MCP_DIR = os.environ.get(
    "FINANCE_MCP_DIR",
    str(Path(__file__).resolve().parents[3] / "finance-mcp"),
)

# MCP 도구 이름 규칙: mcp__{서버이름}__{도구이름}
FINANCE_TOOLS = [
    "mcp__finance__get_quote",
    "mcp__finance__get_financials",
    "mcp__finance__get_filings",
    "mcp__finance__get_news",
]


def finance_mcp_server() -> dict:
    """finance-mcp를 외부 stdio MCP 서버로 붙이는 설정."""
    return {
        "finance": {
            "command": "uv",
            "args": ["run", "--directory", FINANCE_MCP_DIR, "finance-mcp"],
        }
    }
