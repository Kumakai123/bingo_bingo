from typing import Tuple
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult
from analysis.trend_analyzer import TrendAnalyzer


class HighLowAnalyzer(TrendAnalyzer):
    """猜大小趨勢分析：繼承 TrendAnalyzer 共用邏輯"""

    def _get_result(self, draw: DrawResult) -> str:
        return draw.high_low_result or "－"

    def _get_count(self, draw: DrawResult) -> float:
        return float(draw.high_count or 0)

    def _labels(self) -> Tuple[str, str, str]:
        return ("大", "小", "－")

    def _stat_keys(self) -> Tuple[str, str, str]:
        return ("high", "low", "high")
