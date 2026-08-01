"""3주차 — 단일 에이전트 베이스라인.

서브에이전트 없이 모델 하나가 finance-mcp 도구를 조합해 실적 분석을 수행한다.
4주차 팀 구성과 결과를 비교하기 위한 기준점.

실행: uv run python -m earnings_agent baseline AAPL
"""

from __future__ import annotations

from claude_agent_sdk import ClaudeAgentOptions, query

from earnings_agent import report
from earnings_agent.config import FINANCE_TOOLS, finance_mcp_server

SYSTEM_PROMPT = (
    "너는 주식 리서치 애널리스트다. finance 도구로 사실을 수집해 "
    "최근 실적 분석 리포트를 작성한다. 모든 주장에는 수집한 데이터 근거를 붙인다. "
    "투자 조언·매수/매도 추천은 하지 않는다. 리포트 구성: "
    "## 요약 / ## 실적 하이라이트 / ## 긍정 요인 / ## 리스크 요인 / ## 확인 필요한 사실"
)


async def run(ticker: str, market: str = "US") -> str:
    """단일 에이전트로 분석 실행. 도구 호출 과정을 stdout에 로깅하고 리포트를 저장한다."""
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers=finance_mcp_server(),
        allowed_tools=FINANCE_TOOLS,
        max_turns=25,
    )
    prompt = f"{ticker} ({market} 시장) 최근 실적을 분석해 리포트를 작성해줘."

    final_text = ""
    async for message in query(prompt=prompt, options=options):
        for call in report.describe_tool_use(message):
            print(f"  [도구 호출] {call}")
        text = report.extract_text(message)
        if text:
            final_text = text  # 마지막 어시스턴트 텍스트가 리포트
        result = getattr(message, "result", None)
        if result:
            final_text = result

    path = report.save_report(ticker, "baseline", final_text)
    print(f"\n리포트 저장: {path}")
    return final_text
