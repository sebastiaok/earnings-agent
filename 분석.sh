#!/usr/bin/env bash
# 실적 분석 팀 리포트 원커맨드 실행기.
#
#   ./분석.sh AAPL          # 미국 종목, 팀 리포트
#   ./분석.sh 005930 KR     # 한국 종목(6자리 코드), 팀 리포트
#   ./분석.sh JPM US single # 단일 에이전트(baseline)로 빠르게
#
# finance-mcp/.env에서 DART 키를 읽어 하위 프로세스로 전달한다.
set -euo pipefail

TICKER="${1:?사용법: ./분석.sh TICKER [US|KR] [single]}"
MARKET="${2:-US}"
MODE="team"; [ "${3:-}" = "single" ] && MODE="baseline"

FIN="$HOME/project/finance-mcp"
export FINANCE_MCP_NO_VERIFY=1
export FINANCE_MCP_USER_AGENT="finance-mcp sebastiaaa@gmail.com"
# .env의 DART_API_KEY만 안전하게 추출(값에 공백이 없어 cut으로 충분)
if [ -f "$FIN/.env" ]; then
  export DART_API_KEY="$(grep -E '^DART_API_KEY=' "$FIN/.env" | head -1 | cut -d= -f2-)"
fi

cd "$HOME/project/earnings-agent"
export PYTHONUNBUFFERED=1   # 위임/도구 로그를 실시간으로 보이게
echo "▶ ${MODE} 리포트 생성: ${TICKER} (${MARKET}) — 몇 분 걸립니다…"
uv run python -m earnings_agent "$MODE" "$TICKER" --market "$MARKET"
echo "✔ reports/ 폴더에 저장됨"
