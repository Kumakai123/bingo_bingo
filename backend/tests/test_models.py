from datetime import date, datetime
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.draw_result import DrawResult
from app.models.prediction import Prediction
from app.models.crawler_log import CrawlerLog


# ─── DrawResult ────────────────────────────────────────────


class TestDrawResult:
    def _make_draw(self, **overrides):
        defaults = {
            "draw_term": "115009534",
            "draw_date": date(2026, 1, 9),
            "draw_datetime": datetime(2026, 1, 9, 14, 30),
            "numbers_sorted": "11,19,22,24,30,33,34,36,39,41,42,43,44,47,48,59,60,64,68,74",
            "numbers_sequence": "42,68,41,34,30,39,19,47,48,33,22,11,43,60,36,59,24,74,64,44",
            "super_number": "44",
            "high_low_result": "大",
            "high_count": 12,
            "low_count": 8,
            "odd_even_result": "單",
            "odd_count": 11,
            "even_count": 9,
        }
        defaults.update(overrides)
        return DrawResult(**defaults)

    def test_create_and_query(self, db_session):
        draw = self._make_draw()
        db_session.add(draw)
        db_session.commit()

        result = db_session.query(DrawResult).first()
        assert result.draw_term == "115009534"
        assert result.super_number == "44"
        assert result.high_count == 12

    def test_get_numbers_list(self, db_session):
        draw = self._make_draw()
        nums = draw.get_numbers_list()
        assert len(nums) == 20
        assert nums[0] == "11"
        assert nums[-1] == "74"

    def test_get_sequence_list(self, db_session):
        draw = self._make_draw()
        seq = draw.get_sequence_list()
        assert len(seq) == 20
        assert seq[0] == "42"
        assert seq[-1] == "44"

    def test_unique_draw_term(self, db_session):
        db_session.add(self._make_draw())
        db_session.commit()

        db_session.add(self._make_draw())
        with pytest.raises(IntegrityError):
            db_session.commit()


# ─── Prediction ────────────────────────────────────────────


class TestPrediction:
    def test_create(self, db_session):
        pred = Prediction(
            prediction_type="basic",
            period_range=30,
            predicted_numbers='["42","17","08"]',
            based_on_latest_term="115009534",
        )
        db_session.add(pred)
        db_session.commit()

        result = db_session.query(Prediction).first()
        assert result.prediction_type == "basic"
        assert result.period_range == 30


# ─── CrawlerLog ────────────────────────────────────────────


class TestCrawlerLog:
    def test_create(self, db_session):
        log = CrawlerLog(
            started_at=datetime.now(),
            status="success",
            records_fetched=50,
            records_inserted=3,
            records_skipped=47,
        )
        db_session.add(log)
        db_session.commit()

        result = db_session.query(CrawlerLog).first()
        assert result.status == "success"
        assert result.records_inserted == 3
