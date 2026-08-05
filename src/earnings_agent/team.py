"""4주차 — 서브에이전트 팀.

오케스트레이터가 4개 서브에이전트에 위임한다:
  리서처 → (재무 분석가 ‖ 베어) → 에디터

핵심 학습 포인트:
- AgentDefinition의 description이 라우팅을 결정한다 (docstring=프롬프트와 같은 원리).
- 서브에이전트는 독립 컨텍스트에서 실행된다 → 리서처가 수집한 원문이
  오케스트레이터 컨텍스트를 오염시키지 않는다 (컨텍스트 격리).
- 베어 에이전트는 같은 데이터에서 반대 논거를 강제한다 (adversarial 패턴).

실행: uv run python -m earnings_agent team AAPL
모델 라우팅 실험(5주차): EARNINGS_AGENT_CHEAP_MODEL=haiku 로 실행해 비용 비교.
"""

from __future__ import annotations

import os

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

from earnings_agent import report
from earnings_agent.config import FINANCE_TOOLS, finance_mcp_server

# 5주차 모델 라우팅 실험: 수집·편집처럼 판단이 덜 필요한 역할에 작은 모델
_CHEAP = os.environ.get("EARNINGS_AGENT_CHEAP_MODEL")  # 예: "haiku"


def build_agents() -> dict[str, AgentDefinition]:
    """서브에이전트 정의. description을 바꾸면 라우팅이 어떻게 변하는지 실험해볼 것."""
    return {
        "researcher": AgentDefinition(
            description="종목의 공시·재무·뉴스 원데이터를 수집할 때 사용. 분석·해석은 하지 않는다.",
            prompt=(
                "너는 데이터 수집 담당이다. finance 도구로 대상 종목의 시세, 재무, "
                "최근 공시(실적 관련 우선), 뉴스를 수집해 사실만 구조화된 목록으로 정리하라. "
                "재무는 get_financials를 연간(기본)과 분기(period='quarterly') 둘 다 호출해 "
                "최근 분기 실적과 전년 동기 대비(YoY) 수치를 함께 수집하라. "
                "의견·해석·전망을 덧붙이지 마라. 출처(도구·URL)를 항목마다 남겨라."
            ),
            tools=FINANCE_TOOLS,
            model=_CHEAP,
        ),
        "bull-analyst": AgentDefinition(
            description="수집된 데이터에서 강세(긍정) 논거를 구축할 때 사용.",
            prompt=(
                "너는 낙관적 애널리스트다. 주어진 수집 데이터만 근거로 이 종목의 "
                "강세 논거 3~5개를 만들어라. 각 논거에 구체적 숫자·사실을 인용하라. "
                "데이터에 없는 내용을 지어내지 마라."
            ),
            tools=[],
        ),
        "bear-analyst": AgentDefinition(
            description="수집된 데이터에서 약세(부정)·리스크 논거를 구축할 때 사용. 강세 논거에 대한 반론 담당.",
            prompt=(
                "너는 회의적 애널리스트다. 주어진 수집 데이터만 근거로 이 종목의 "
                "약세 논거·리스크 3~5개를 만들어라. 낙관 논거의 약점을 지적하라. "
                "각 논거에 구체적 숫자·사실을 인용하라. 데이터에 없는 내용을 지어내지 마라."
            ),
            tools=[],
        ),
        "editor": AgentDefinition(
            description="강세/약세 논거를 받아 최종 리포트로 통합·팩트체크할 때 사용. 마지막 단계.",
            prompt=(
                "너는 편집장이다. 수집 데이터, 강세 논거, 약세 논거를 받아 "
                "마크다운 리포트로 통합하라. 구성: ## 요약 / ## 실적 하이라이트 / "
                "## 강세 논거 / ## 약세 논거 / ## 확인 필요한 사실. "
                "수집 데이터에 근거 없는 주장은 삭제하거나 '확인 필요'로 옮겨라. "
                "투자 추천 문구는 넣지 않는다."
            ),
            tools=[],
            model=_CHEAP,
        ),
    }


ORCHESTRATOR_PROMPT = (
    "너는 리서치 팀장이다. 아래 순서로 서브에이전트에 위임해 {ticker}({market}) 실적 분석 리포트를 완성하라.\n"
    "1) researcher에게 데이터 수집을 맡긴다.\n"
    "2) 수집 결과를 bull-analyst와 bear-analyst 양쪽에 전달해 각각 논거를 만들게 한다.\n"
    "3) 세 결과물을 editor에게 넘겨 최종 리포트를 받는다.\n"
    "최종 응답은 editor의 리포트 전문만 출력한다."
)


async def run(ticker: str, market: str = "US") -> str:
    options = ClaudeAgentOptions(
        mcp_servers=finance_mcp_server(),
        allowed_tools=FINANCE_TOOLS + ["Agent"],
        agents=build_agents(),
        max_turns=40,
    )
    final_text = ""
    async for message in query(
        prompt=ORCHESTRATOR_PROMPT.format(ticker=ticker, market=market), options=options
    ):
        for call in report.describe_tool_use(message):
            print(f"  [위임/도구] {call}")
        text = report.extract_text(message)
        if text:
            final_text = text
        result = getattr(message, "result", None)
        if result:
            final_text = result

    path = report.save_report(ticker, "team", final_text)
    print(f"\n리포트 저장: {path}")
    return final_text
