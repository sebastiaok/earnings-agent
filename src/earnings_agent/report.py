"""리포트 저장·메시지 스트림 처리 (순수 함수 — 테스트 대상)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"


def report_path(ticker: str, mode: str, run_date: date | None = None) -> Path:
    d = (run_date or date.today()).isoformat()
    return REPORTS_DIR / f"{ticker.upper()}_{mode}_{d}.md"


def extract_text(message: object) -> str:
    """SDK 메시지에서 텍스트 블록만 추출. AssistantMessage.content의 TextBlock.text를 모은다."""
    parts: list[str] = []
    for block in getattr(message, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


def describe_tool_use(message: object) -> list[str]:
    """메시지에서 도구 호출 내역을 '도구명(입력요약)' 형태로 추출 — 관찰 로그용."""
    out: list[str] = []
    for block in getattr(message, "content", []) or []:
        name = getattr(block, "name", None)
        if name and hasattr(block, "input"):
            args = getattr(block, "input", {}) or {}
            summary = ", ".join(f"{k}={v}" for k, v in list(args.items())[:3])
            out.append(f"{name}({summary})")
    return out


def save_report(ticker: str, mode: str, body: str) -> Path:
    path = report_path(ticker, mode)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path
