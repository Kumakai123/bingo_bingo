from typing import Tuple
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult
from analysis.trend_analyzer import TrendAnalyzer


class OddEvenAnalyzer(TrendAnalyzer):
    """猜單雙趨勢分析：繼承 TrendAnalyzer 共用邏輯"""

    def _get_result(self, draw: DrawResult) -> str:
        return draw.odd_even_result or "－"

    def _get_count(self, draw: DrawResult) -> float:
        return float(draw.odd_count or 0)

    def _labels(self) -> Tuple[str, str, str]:
        return ("單", "雙", "－")

    def _stat_keys(self) -> Tuple[str, str, str]:
        return ("odd", "even", "odd")
