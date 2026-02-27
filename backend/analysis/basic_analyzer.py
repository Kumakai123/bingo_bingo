import math
from collections import Counter
from typing import Dict, List, Set
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult

DECAY_RATE = 0.05


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
        repeat_info = self._repeat_tracking(draws)
        consecutive_hits = self._consecutive_draw_tracking(draws)

        return {
            "predictions": top,
            "all_stats": all_stats,
            "repeat_info": repeat_info,
            "consecutive_hits": consecutive_hits,
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
        """指數衰減加權：weight = e^(-DECAY_RATE * idx)"""
        freq: Dict[str, float] = {}
        for idx, draw in enumerate(draws):
            weight = math.exp(-DECAY_RATE * idx)
            for num in draw.numbers_sorted.split(","):
                freq[num] = freq.get(num, 0.0) + weight
        return freq

    def _repeat_tracking(self, draws) -> Dict:
        """追蹤最近一期有多少號碼在前一期也出現"""
        if len(draws) < 2:
            return {"repeat_count": 0, "repeat_numbers": []}

        latest = set(draws[0].get_numbers_list())
        previous = set(draws[1].get_numbers_list())
        repeats = sorted(latest & previous)

        return {
            "repeat_count": len(repeats),
            "repeat_numbers": repeats,
            "latest_term": draws[0].draw_term,
            "previous_term": draws[1].draw_term,
        }

    def _consecutive_draw_tracking(self, draws) -> List[Dict]:
        """標記連續 2 期、3 期都出現的號碼"""
        if len(draws) < 2:
            return []

        num_sets: List[Set[str]] = [set(d.get_numbers_list()) for d in draws]

        consec_2 = sorted(num_sets[0] & num_sets[1]) if len(num_sets) >= 2 else []
        consec_3 = sorted(num_sets[0] & num_sets[1] & num_sets[2]) if len(num_sets) >= 3 else []

        result = []
        for num in sorted(num_sets[0]):
            streak = 1
            for s in num_sets[1:]:
                if num in s:
                    streak += 1
                else:
                    break
            if streak >= 2:
                result.append({"number": num, "consecutive_draws": streak})

        return sorted(result, key=lambda x: x["consecutive_draws"], reverse=True)

    # ─── Helpers ──────────────────────────────────────────

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(limit)
            .all()
        )

    def _build_all_stats(self, draws, total: int) -> Dict:
        expected_value = total * 20 / 80

        stats = {
            f"{i:02d}": {
                "count": 0,
                "pct": 0.0,
                "last_term": None,
                "expected_value": round(expected_value, 2),
                "deviation_pct": 0.0,
            }
            for i in range(1, 81)
        }
        for draw in draws:
            for num in draw.numbers_sorted.split(","):
                stats[num]["count"] += 1
                if stats[num]["last_term"] is None:
                    stats[num]["last_term"] = draw.draw_term

        for num, s in stats.items():
            s["pct"] = round(s["count"] / total * 100, 2) if total else 0.0
            if expected_value > 0:
                s["deviation_pct"] = round(
                    (s["count"] - expected_value) / expected_value * 100, 2
                )

        return stats

    def _empty_result(self) -> Dict:
        return {
            "predictions": [],
            "all_stats": {},
            "repeat_info": {"repeat_count": 0, "repeat_numbers": []},
            "consecutive_hits": [],
            "period_range": 0,
            "method": "none",
        }
