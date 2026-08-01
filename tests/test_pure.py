"""네트워크·SDK 실행 없이 도는 단위 테스트 (순수 함수만)."""

from datetime import date

from earnings_agent import judge, report


class FakeBlock:
    def __init__(self, text=None, name=None, input=None):
        if text is not None:
            self.text = text
        if name is not None:
            self.name = name
            self.input = input or {}


class FakeMessage:
    def __init__(self, blocks):
        self.content = blocks


def test_extract_text():
    msg = FakeMessage([FakeBlock(text="안녕 "), FakeBlock(text="리포트")])
    assert report.extract_text(msg) == "안녕 리포트"
    assert report.extract_text(FakeMessage([])) == ""
    assert report.extract_text(object()) == ""


def test_describe_tool_use():
    msg = FakeMessage([FakeBlock(name="mcp__finance__get_quote", input={"ticker": "AAPL", "market": "US"})])
    calls = report.describe_tool_use(msg)
    assert calls == ["mcp__finance__get_quote(ticker=AAPL, market=US)"]


def test_report_path():
    p = report.report_path("aapl", "team", date(2026, 7, 6))
    assert p.name == "AAPL_team_2026-07-06.md"


def test_parse_scores_clean():
    text = '{"specificity": 4, "balance": 3, "grounding": 5, "actionability": 4, "comment": "좋음"}'
    scores = judge.parse_scores(text)
    assert scores is not None
    assert judge.total_score(scores) == 16


def test_parse_scores_with_surrounding_text():
    text = '채점 결과입니다:\n{"specificity": 2, "balance": 2, "grounding": 3, "actionability": 1, "comment": "부족"}\n감사합니다'
    scores = judge.parse_scores(text)
    assert scores is not None
    assert judge.total_score(scores) == 8


def test_parse_scores_invalid():
    assert judge.parse_scores("JSON 없음") is None
    assert judge.parse_scores('{"specificity": 4}') is None  # 필수 키 부족
