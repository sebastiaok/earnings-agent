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

## 평가 결과 (2026-08-01)

동일 루브릭(specificity·balance·grounding·actionability, 각 5점=20점 만점)으로
단일(baseline) vs 팀(team)을 3종목·2시장·2섹터에서 채점:

| 종목 | 시장 | 섹터 | baseline | team | Δ | baseline 감점 축 |
|---|---|---|---|---|---|---|
| AAPL | US | 테크 | 19 | 20 | +1 | balance |
| JPM | US | 금융 | 19 | 20 | +1 | balance |
| 삼성전자(005930) | KR | 테크 | 19 | 20 | +1 | balance |

**세 종목 모두 팀이 +1, 잃은 점은 언제나 `balance`(강세/약세 균형).** 멀티 에이전트의 우위가
`bear`(반대 논거 강제) + `editor`(팩트체크) 분리가 노린 축에 재현성 있게 위치했다.
editor는 강세 논거의 지표 간 항등식 불성립(예: PER×ROE≠PBR)을 잡아 '확인 필요'로 강등하기도 했다.

**모델 라우팅**: researcher·editor를 Haiku로 내리면 balance는 유지되나 `grounding`이 감점(5→4).
→ 수집(researcher)=작은 모델 안전, 검증(editor)=강한 모델 유지가 결론.

**도구 격리(부수 발견)**: baseline(단일)은 finance-mcp 데이터가 얇은 도메인(은행·KR)에서
세션에 연결된 앰비언트 MCP 도구를 끌어씀(`allowed_tools` 화이트리스트가 최상위 에이전트엔 미강제).
반면 team의 서브에이전트는 `AgentDefinition.tools`로 강제 제한 → 외부 도구 누출 0.
멀티 에이전트는 품질뿐 아니라 **도구 권한 격리**라는 구조적 이득을 준다.

> 주의: LLM-as-judge는 관대·긴글선호 편향이 있어 절대점수보다 **축별 차이의 방향성**을 신뢰.
> n=3의 소표본이므로 경향 참고용. 리포트 원본은 로컬 `reports/`(gitignore)에서 생성.

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
