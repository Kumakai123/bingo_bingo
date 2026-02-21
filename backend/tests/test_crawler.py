from datetime import date, datetime
from unittest.mock import patch, MagicMock
import pytest

from app.models.draw_result import DrawResult
from app.models.crawler_log import CrawlerLog
from crawler.bingo_crawler import BingoCrawler


# ─── Sample API data ─────────────────────────────────────────

VALID_DRAW = {
    "drawTerm": 115009534,
    "bigShowOrder": [
        "11", "19", "22", "24", "30", "33", "34", "36", "39", "41",
        "42", "43", "44", "47", "48", "59", "60", "64", "68", "74",
    ],
    "openShowOrder": [
        "42", "68", "41", "34", "30", "39", "19", "47", "48", "33",
        "22", "11", "43", "60", "36", "59", "24", "74", "64", "44",
    ],
    "bullEyeTop": "44",
    "highLowTop": "大",
    "oddEvenTop": "單",
}


# ─── Validation Tests ────────────────────────────────────────


class TestValidate:
    def setup_method(self):
        self.crawler = BingoCrawler(db_session=MagicMock())

    def test_valid_data_passes(self):
        assert self.crawler._validate(VALID_DRAW) is True

    def test_missing_field_fails(self):
        data = {**VALID_DRAW}
        del data["drawTerm"]
        assert self.crawler._validate(data) is False

    def test_wrong_count_fails(self):
        data = {**VALID_DRAW, "openShowOrder": ["01"] * 19}
        assert self.crawler._validate(data) is False

    def test_bullseye_mismatch_fails(self):
        data = {**VALID_DRAW, "bullEyeTop": "99"}
        assert self.crawler._validate(data) is False

    def test_out_of_range_fails(self):
        seq = list(VALID_DRAW["openShowOrder"])
        seq[0] = "81"
        data = {**VALID_DRAW, "openShowOrder": seq}
        assert self.crawler._validate(data) is False

    def test_duplicate_numbers_fails(self):
        seq = list(VALID_DRAW["openShowOrder"])
        seq[1] = seq[0]  # duplicate
        data = {**VALID_DRAW, "openShowOrder": seq}
        assert self.crawler._validate(data) is False

    def test_non_numeric_fails(self):
        seq = list(VALID_DRAW["openShowOrder"])
        seq[0] = "XX"
        data = {**VALID_DRAW, "openShowOrder": seq}
        assert self.crawler._validate(data) is False


# ─── Parse Tests ─────────────────────────────────────────────


class TestParseDraw:
    def setup_method(self):
        self.crawler = BingoCrawler(db_session=MagicMock())

    def test_parse_basic_fields(self):
        result = self.crawler._parse_draw_data(VALID_DRAW)
        assert result["draw_term"] == "115009534"
        assert result["super_number"] == "44"
        assert result["numbers_sorted"] == ",".join(VALID_DRAW["bigShowOrder"])
        assert result["numbers_sequence"] == ",".join(VALID_DRAW["openShowOrder"])

    def test_parse_high_low_counts(self):
        result = self.crawler._parse_draw_data(VALID_DRAW)
        # numbers 41-80: 41,42,43,44,47,48,59,60,64,68,74 = 11
        # numbers 01-40: 11,19,22,24,30,33,34,36,39 = 9
        assert result["high_count"] + result["low_count"] == 20
        assert result["high_count"] == 11
        assert result["low_count"] == 9

    def test_parse_odd_even_counts(self):
        result = self.crawler._parse_draw_data(VALID_DRAW)
        assert result["odd_count"] + result["even_count"] == 20
        # odd: 11,19,33,39,41,43,47,59 = 8? let's count
        # 11✓ 19✓ 22✗ 24✗ 30✗ 33✓ 34✗ 36✗ 39✓ 41✓ 42✗ 43✓ 44✗ 47✓ 48✗ 59✓ 60✗ 64✗ 68✗ 74✗
        # odd = 8, even = 12
        assert result["odd_count"] == 8
        assert result["even_count"] == 12

    def test_parse_high_low_result(self):
        result = self.crawler._parse_draw_data(VALID_DRAW)
        assert result["high_low_result"] == "大"

    def test_parse_odd_even_result(self):
        result = self.crawler._parse_draw_data(VALID_DRAW)
        assert result["odd_even_result"] == "單"

    def test_parse_draw_date(self):
        result = self.crawler._parse_draw_data(VALID_DRAW)
        # 115 = 民國 115 -> 2026, day 009 -> Jan 9
        assert result["draw_date"] == date(2026, 1, 9)


# ─── Save Tests ──────────────────────────────────────────────


class TestParseAndSave:
    def test_insert_new(self, db_session):
        crawler = BingoCrawler(db_session=db_session)
        result = crawler.parse_and_save(VALID_DRAW)
        assert result == "inserted"
        assert db_session.query(DrawResult).count() == 1

    def test_skip_duplicate(self, db_session):
        crawler = BingoCrawler(db_session=db_session)
        crawler.parse_and_save(VALID_DRAW)
        result = crawler.parse_and_save(VALID_DRAW)
        assert result == "skipped"
        assert db_session.query(DrawResult).count() == 1

    def test_fail_invalid(self, db_session):
        crawler = BingoCrawler(db_session=db_session)
        bad_data = {**VALID_DRAW, "openShowOrder": ["01"] * 19}
        result = crawler.parse_and_save(bad_data)
        assert result == "failed"
        assert db_session.query(DrawResult).count() == 0


# ─── Fetch Tests (mocked HTTP) ───────────────────────────────


class TestFetchLatestDraws:
    @patch("crawler.bingo_crawler.requests.Session")
    def test_fetch_returns_draws(self, MockSession):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "rtCode": 0,
            "content": {"bingoQueryResult": [VALID_DRAW]},
        }
        mock_resp.raise_for_status = MagicMock()

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_resp
        MockSession.return_value = mock_session_instance

        crawler = BingoCrawler(db_session=MagicMock())
        results = crawler.fetch_latest_draws()

        assert len(results) >= 1
        assert results[0]["drawTerm"] == 115009534

    @patch("crawler.bingo_crawler.requests.Session")
    def test_fetch_handles_api_error(self, MockSession):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"rtCode": 1, "rtMsg": "error"}
        mock_resp.raise_for_status = MagicMock()

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_resp
        MockSession.return_value = mock_session_instance

        crawler = BingoCrawler(db_session=MagicMock())
        results = crawler.fetch_latest_draws()
        assert results == []
