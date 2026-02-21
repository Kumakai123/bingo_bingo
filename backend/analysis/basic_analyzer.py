from collections import Counter
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult


class BasicAnalyzer:
    """基本玩法：統計 01-80 號碼出現頻率，預測高機率號碼"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(
        self,
        period_range: int = 30,
        top_n: int = 10,
        use_weighted: bool = True,
    ) -> Dict:
        draws = self._fetch_draws(period_range)
        if not draws:
            return self._empty_result()

        freq = (
            self._weighted_frequency(draws)
            if use_weighted
            else self._simple_frequency(draws)
        )

        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        all_stats = self._build_all_stats(draws, len(draws))

        return {
            "predictions": top,
            "all_stats": all_stats,
            "period_range": len(draws),
            "method": "weighted" if use_weighted else "simple",
        }

    def batch_analyze(
        self,
        period_ranges: List[int] = [10, 20, 30, 50, 100],
        top_n: int = 10,
        use_weighted: bool = True,
    ) -> Dict[int, Dict]:
        return {
            p: self.analyze(p, top_n, use_weighted) for p in period_ranges
        }

    # ─── Algorithms ───────────────────────────────────────

    def _simple_frequency(self, draws) -> Dict[str, int]:
        counter = Counter()
        for draw in draws:
            counter.update(draw.numbers_sorted.split(","))
        return dict(counter)

    def _weighted_frequency(self, draws) -> Dict[str, float]:
        WEIGHTS = {(0, 10): 3.0, (10, 20): 2.0, (20, 30): 1.5}
        freq: Dict[str, float] = {}

        for idx, draw in enumerate(draws):
            weight = 1.0
            for (lo, hi), w in WEIGHTS.items():
                if lo <= idx < hi:
                    weight = w
                    break

            for num in draw.numbers_sorted.split(","):
                freq[num] = freq.get(num, 0.0) + weight

        return freq

    # ─── Helpers ──────────────────────────────────────────

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_datetime.desc())
            .limit(limit)
            .all()
        )

    def _build_all_stats(self, draws, total: int) -> Dict:
        stats = {
            f"{i:02d}": {"count": 0, "pct": 0.0, "last_term": None}
            for i in range(1, 81)
        }
        for draw in draws:
            for num in draw.numbers_sorted.split(","):
                stats[num]["count"] += 1
                if stats[num]["last_term"] is None:
                    stats[num]["last_term"] = draw.draw_term

        for num, s in stats.items():
            s["pct"] = round(s["count"] / total * 100, 2) if total else 0.0

        return stats

    def _empty_result(self) -> Dict:
        return {
            "predictions": [],
            "all_stats": {},
            "period_range": 0,
            "method": "none",
        }
