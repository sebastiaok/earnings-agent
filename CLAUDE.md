# earnings-agent — 클로드 작업 지시문

## 프로젝트 개요
어닝콜/실적 분석 멀티 에이전트. 5주 로드맵의 2단계 (3~5주차).
1단계 finance-mcp(`/Users/a05034/project/finance-mcp`)를 외부 MCP 서버로 사용한다.
문서(로드맵·진행로그·학습가이드)는 Obsidian 볼트:
`/Users/a05034/Documents/Obsidian Vault/21_VibeCoding/프로젝트/리서치MCP서버/`

## 구조 (주차별 진행)
- `baseline.py` — 3주차: 단일 에이전트 (비교 기준점)
- `team.py` — 4주차: 서브에이전트 4개 (researcher → bull ‖ bear → editor)
- `judge.py` — 5주차: LLM-as-judge 채점 (baseline vs team 비교)
- `report.py` — 메시지 스트림 처리·리포트 저장 (순수 함수, 테스트 대상)
- `config.py` — finance-mcp 연결 설정 (FINANCE_MCP_DIR)

## 아키텍처 규칙
- SDK 호출부(run)와 순수 로직(파싱·포맷·경로)을 분리한다. 테스트는 순수 로직만.
- 서브에이전트 description은 "언제 쓰는지"를 기준으로 쓴다 — 라우팅을 결정하는 프롬프트다.
- bull/bear 에이전트에는 도구를 주지 않는다 (수집 데이터만 근거로 논거 구성 → 환각 억제).
- 리포트는 reports/{TICKER}_{mode}_{date}.md — baseline과 team을 같은 형식으로 저장해 비교.

## 개발 명령어
```bash
uv sync
uv run pytest                                        # 순수 함수 테스트
uv run python -m earnings_agent baseline AAPL        # 3주차
uv run python -m earnings_agent team AAPL            # 4주차
uv run python -m earnings_agent judge reports/<파일>  # 5주차
EARNINGS_AGENT_CHEAP_MODEL=haiku uv run python -m earnings_agent team AAPL  # 모델 라우팅 실험
```

## 하지 말 것
- 자동 매매·투자 추천 기능 금지 (리포트에도 매수/매도 문구 금지)
- 테스트에서 query() 실호출 금지 (비용·비결정성)
- 웹 UI 금지 (범위 밖)

## 진행 로그 규칙
작업 세션 종료 시 볼트의 `01_진행로그.md`에 날짜·작업·배운 점·다음 할 일 기록.
