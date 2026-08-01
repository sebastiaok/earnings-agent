"""5주차 — LLM-as-judge 평가.

리포트 md 파일을 루브릭으로 채점한다 (도구 없이 순수 추론).
baseline vs team 리포트를 같은 루브릭으로 채점해 멀티 에이전트가
실제로 나은지 검증하는 것이 5주차의 핵심.

실행: uv run python -m earnings_agent judge reports/AAPL_team_2026-XX-XX.md
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, query

from earnings_agent import report

RUBRIC = """다음 주식 리서치 리포트를 루브릭으로 채점하라.

각 항목 1~5점:
- specificity: 주장에 구체적 숫자·출처가 붙어 있는가
- balance: 강세/약세 논거가 균형 있게 다뤄졌는가
- grounding: 근거 없는 주장(환각 의심)이 없는가
- actionability: '확인 필요한 사실'이 후속 조사 가능한 수준으로 구체적인가

반드시 아래 JSON만 출력하라 (설명 금지):
{"specificity": n, "balance": n, "grounding": n, "actionability": n, "comment": "한 줄 총평"}

--- 리포트 ---
"""


def parse_scores(text: str) -> dict | None:
    """judge 응답에서 JSON 추출 (순수 함수 — 테스트 대상).

    모델이 JSON 앞뒤에 텍스트를 붙이는 경우를 방어한다.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return None
    required = {"specificity", "balance", "grounding", "actionability"}
    if not required.issubset(data.keys()):
        return None
    return data


def total_score(scores: dict) -> int:
    return sum(int(scores[k]) for k in ("specificity", "balance", "grounding", "actionability"))


async def run(report_path: str) -> dict | None:
    body = Path(report_path).read_text(encoding="utf-8")
    options = ClaudeAgentOptions(max_turns=1)  # 도구 없음 — 순수 채점
    final_text = ""
    async for message in query(prompt=RUBRIC + body, options=options):
        text = report.extract_text(message)
        if text:
            final_text = text
        result = getattr(message, "result", None)
        if result:
            final_text = result

    scores = parse_scores(final_text)
    if scores is None:
        print(f"채점 파싱 실패. 원문:\n{final_text}")
        return None
    print(json.dumps(scores, ensure_ascii=False, indent=2))
    print(f"총점: {total_score(scores)}/20")
    return scores
