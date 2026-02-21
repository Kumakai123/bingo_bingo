from datetime import date, datetime
import pytest

from app.models.draw_result import DrawResult
from analysis.basic_analyzer import BasicAnalyzer
from analysis.super_number_analyzer import SuperNumberAnalyzer
from analysis.high_low_analyzer import HighLowAnalyzer
from analysis.odd_even_analyzer import OddEvenAnalyzer


# ─── Test Helpers ─────────────────────────────────────────────


def _make_draw(db, draw_term, numbers_sorted, super_number="44",
               high_low="大", odd_even="單", high_count=12, low_count=8,
               odd_count=11, even_count=9, dt_offset=0):
    """Insert a draw record for testing."""
    draw = DrawResult(
        draw_term=draw_term,
        draw_date=date(2026, 1, 9),
        draw_datetime=datetime(2026, 1, 9, 14, 30 - dt_offset),
        numbers_sorted=numbers_sorted,
        numbers_sequence=numbers_sorted,  # reuse for simplicity
        super_number=super_number,
        high_low_result=high_low,
        high_count=high_count,
        low_count=low_count,
        odd_even_result=odd_even,
        odd_count=odd_count,
        even_count=even_count,
    )
    db.add(draw)
    db.commit()
    return draw


def _seed_draws(db, count=5, high_low_pattern=None, odd_even_pattern=None,
                super_numbers=None):
    """Seed N draws with controllable patterns."""
    for i in range(count):
        hl = high_low_pattern[i] if high_low_pattern else "大"
        oe = odd_even_pattern[i] if odd_even_pattern else "單"
        sn = super_numbers[i] if super_numbers else "44"
        _make_draw(
            db,
            draw_term=f"11500{i:04d}",
            numbers_sorted="01,02,03,04,05,41,42,43,44,45,06,07,08,09,10,46,47,48,49,50",
            super_number=sn,
            high_low=hl,
            odd_even=oe,
            high_count=10,
            low_count=10,
            odd_count=10,
            even_count=10,
            dt_offset=i,  # older draws have smaller datetime
        )


# ─── BasicAnalyzer ────────────────────────────────────────────


class TestBasicAnalyzer:
    def test_empty_draws(self, db_session):
        result = BasicAnalyzer(db_session).analyze(30)
        assert result["predictions"] == []
        assert result["period_range"] == 0
        assert result["method"] == "none"

    def test_simple_frequency(self, db_session):
        _seed_draws(db_session, count=3)
        result = BasicAnalyzer(db_session).analyze(10, top_n=5, use_weighted=False)
        assert result["method"] == "simple"
        assert result["period_range"] == 3
        assert len(result["predictions"]) == 5
        # Each number appears 3 times (once per draw)
        assert result["predictions"][0][1] == 3

    def test_weighted_higher_for_recent(self, db_session):
        # Insert 2 draws: draw 0 is recent (weight 3.0), draw 1 is older
        _make_draw(db_session, "115000001", "01,02,03,04,05,06,07,08,09,10,41,42,43,44,45,46,47,48,49,50",
                   dt_offset=0)
        _make_draw(db_session, "115000002", "01,02,03,04,05,06,07,08,09,10,41,42,43,44,45,46,47,48,49,50",
                   dt_offset=1)
        result = BasicAnalyzer(db_session).analyze(10, top_n=5, use_weighted=True)
        assert result["method"] == "weighted"
        # Both within top-10 range so weight=3.0 each → score = 6.0
        assert result["predictions"][0][1] == 6.0

    def test_all_stats_has_80_entries(self, db_session):
        _seed_draws(db_session, count=1)
        result = BasicAnalyzer(db_session).analyze(10)
        assert len(result["all_stats"]) == 80

    def test_batch_analyze(self, db_session):
        _seed_draws(db_session, count=5)
        result = BasicAnalyzer(db_session).batch_analyze([10, 20], top_n=5)
        assert 10 in result
        assert 20 in result
        assert len(result[10]["predictions"]) == 5


# ─── SuperNumberAnalyzer ──────────────────────────────────────


class TestSuperNumberAnalyzer:
    def test_empty_draws(self, db_session):
        result = SuperNumberAnalyzer(db_session).analyze(30)
        assert result["predictions"] == []
        assert result["period_range"] == 0

    def test_frequency(self, db_session):
        _seed_draws(db_session, count=5, super_numbers=["44", "44", "07", "44", "07"])
        result = SuperNumberAnalyzer(db_session).analyze(10, top_n=3)
        assert result["period_range"] == 5
        # 44 appears 3 times, 07 appears 2 times
        assert result["predictions"][0] == ("44", 3)
        assert result["predictions"][1] == ("07", 2)

    def test_all_stats_has_80_entries(self, db_session):
        _seed_draws(db_session, count=1)
        result = SuperNumberAnalyzer(db_session).analyze(10)
        assert len(result["all_stats"]) == 80


# ─── HighLowAnalyzer ─────────────────────────────────────────


class TestHighLowAnalyzer:
    def test_empty_draws(self, db_session):
        result = HighLowAnalyzer(db_session).analyze(30)
        assert result["prediction"] is None

    def test_streak_reversal(self, db_session):
        """3+ consecutive same result → predict opposite"""
        _seed_draws(db_session, count=5, high_low_pattern=["大", "大", "大", "小", "小"])
        result = HighLowAnalyzer(db_session).analyze(10)
        assert result["prediction"] == "小"
        assert result["confidence"] == 0.60

    def test_streak_4_higher_confidence(self, db_session):
        _seed_draws(db_session, count=5, high_low_pattern=["大", "大", "大", "大", "小"])
        result = HighLowAnalyzer(db_session).analyze(10)
        assert result["prediction"] == "小"
        assert result["confidence"] == 0.65

    def test_ratio_imbalance_high(self, db_session):
        """High ratio > 70% → predict low (no streak of 3+ to interfere)"""
        _seed_draws(db_session, count=10,
                    high_low_pattern=["大", "大", "小", "大", "大", "小", "大", "大", "大", "大"])
        result = HighLowAnalyzer(db_session).analyze(10)
        assert result["prediction"] == "小"
        assert result["confidence"] == 0.65

    def test_majority_fallback(self, db_session):
        """Neither streak nor imbalance → majority wins"""
        _seed_draws(db_session, count=5, high_low_pattern=["大", "小", "大", "小", "大"])
        result = HighLowAnalyzer(db_session).analyze(10)
        assert result["prediction"] == "大"
        assert result["confidence"] == 0.52

    def test_stats_populated(self, db_session):
        _seed_draws(db_session, count=3, high_low_pattern=["大", "小", "大"])
        result = HighLowAnalyzer(db_session).analyze(10)
        assert result["statistics"]["high_count"] == 2
        assert result["statistics"]["low_count"] == 1


# ─── OddEvenAnalyzer ─────────────────────────────────────────


class TestOddEvenAnalyzer:
    def test_empty_draws(self, db_session):
        result = OddEvenAnalyzer(db_session).analyze(30)
        assert result["prediction"] is None

    def test_streak_reversal(self, db_session):
        _seed_draws(db_session, count=4, odd_even_pattern=["單", "單", "單", "雙"])
        result = OddEvenAnalyzer(db_session).analyze(10)
        assert result["prediction"] == "雙"
        assert result["confidence"] == 0.60

    def test_majority_fallback(self, db_session):
        _seed_draws(db_session, count=5, odd_even_pattern=["單", "雙", "單", "雙", "單"])
        result = OddEvenAnalyzer(db_session).analyze(10)
        assert result["prediction"] == "單"
        assert result["confidence"] == 0.52

    def test_stats_populated(self, db_session):
        _seed_draws(db_session, count=4, odd_even_pattern=["單", "雙", "單", "雙"])
        result = OddEvenAnalyzer(db_session).analyze(10)
        assert result["statistics"]["odd_count"] == 2
        assert result["statistics"]["even_count"] == 2
