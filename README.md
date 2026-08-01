# earnings-agent

Claude Agent SDK 기반 실적 분석 멀티 에이전트 (학습 프로젝트 2단계).
[finance-mcp](../finance-mcp)를 도구 서버로 사용한다.

## 아키텍처

```
오케스트레이터 (team.py)
├── researcher    — finance-mcp 도구로 데이터 수집 (해석 금지)
├── bull-analyst  — 강세 논거 (도구 없음, 수집 데이터만 근거)
├── bear-analyst  — 약세 논거·반론 (도구 없음)
└── editor        — 팩트체크 + 최종 리포트 통합
```

`baseline.py`는 같은 작업을 단일 에이전트로 수행 — 멀티 에이전트가 실제로 나은지
`judge.py`(LLM-as-judge, 20점 루브릭)로 비교하는 것이 이 프로젝트의 핵심 실험.

## 실행

```bash
uv sync
uv run pytest

# 사전 조건: Claude Code CLI 로그인 상태 (SDK가 인증을 공유)
#           finance-mcp가 ../finance-mcp에 있거나 FINANCE_MCP_DIR 지정

uv run python -m earnings_agent baseline AAPL       # 3주차: 단일 에이전트
uv run python -m earnings_agent team AAPL           # 4주차: 서브에이전트 팀
uv run python -m earnings_agent team 005930 --market KR
uv run python -m earnings_agent judge reports/AAPL_team_<날짜>.md   # 5주차: 채점
```

## 환경변수

- `FINANCE_MCP_DIR` — finance-mcp 경로 (기본 `../finance-mcp`)
- `EARNINGS_AGENT_CHEAP_MODEL` — researcher/editor에 쓸 작은 모델 (예: `haiku`) — 비용 라우팅 실험
- `DART_API_KEY` — KR 종목 분석 시 필요 (finance-mcp로 전달됨)
