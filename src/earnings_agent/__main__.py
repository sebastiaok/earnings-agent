"""CLI 엔트리포인트.

uv run python -m earnings_agent baseline AAPL          # 3주차
uv run python -m earnings_agent team AAPL              # 4주차
uv run python -m earnings_agent team 005930 --market KR
uv run python -m earnings_agent judge reports/AAPL_team_2026-07-06.md   # 5주차
"""

from __future__ import annotations

import argparse
import asyncio


def main() -> None:
    parser = argparse.ArgumentParser(prog="earnings_agent")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_base = sub.add_parser("baseline", help="단일 에이전트 (3주차)")
    p_base.add_argument("ticker")
    p_base.add_argument("--market", default="US", choices=["US", "KR"])

    p_team = sub.add_parser("team", help="서브에이전트 팀 (4주차)")
    p_team.add_argument("ticker")
    p_team.add_argument("--market", default="US", choices=["US", "KR"])

    p_judge = sub.add_parser("judge", help="리포트 채점 (5주차)")
    p_judge.add_argument("report_path")

    args = parser.parse_args()

    if args.mode == "baseline":
        from earnings_agent import baseline

        asyncio.run(baseline.run(args.ticker, args.market))
    elif args.mode == "team":
        from earnings_agent import team

        asyncio.run(team.run(args.ticker, args.market))
    elif args.mode == "judge":
        from earnings_agent import judge

        asyncio.run(judge.run(args.report_path))


if __name__ == "__main__":
    main()
