from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult


class ConsecutiveNumberAnalyzer:
    """連號分析：統計同一期內數值相差 1 的號碼對"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(self, period_range: int = 30) -> Dict:
        draws = self._fetch_draws(period_range)
        if not draws:
            return self._empty_result()

        total = len(draws)
        pair_counts: List[int] = []
        all_draw_pairs: List[Dict] = []

        for draw in draws:
            nums = sorted(int(n) for n in draw.get_numbers_list())
            pairs = self._find_consecutive_pairs(nums)
            pair_counts.append(len(pairs))
            all_draw_pairs.append({
                "draw_term": draw.draw_term,
                "pair_count": len(pairs),
                "pairs": pairs,
            })

        avg_pairs = round(sum(pair_counts) / total, 2)
        max_pairs = max(pair_counts)
        min_pairs = min(pair_counts)
        zero_pair_draws = sum(1 for c in pair_counts if c == 0)
        high_pair_draws = sum(1 for c in pair_counts if c >= 4)

        latest = all_draw_pairs[0] if all_draw_pairs else None

        return {
            "statistics": {
                "avg_pairs": avg_pairs,
                "max_pairs": max_pairs,
                "min_pairs": min_pairs,
                "zero_pair_rate": round(zero_pair_draws / total * 100, 2),
                "high_pair_rate": round(high_pair_draws / total * 100, 2),
            },
            "latest_draw": latest,
            "period_range": total,
        }

    def _find_consecutive_pairs(self, sorted_nums: List[int]) -> List[Tuple[int, int]]:
        pairs = []
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i + 1] - sorted_nums[i] == 1:
                pairs.append((sorted_nums[i], sorted_nums[i + 1]))
        return pairs

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(limit)
            .all()
        )

    def _empty_result(self) -> Dict:
        return {
            "statistics": {
                "avg_pairs": 0,
                "max_pairs": 0,
                "min_pairs": 0,
                "zero_pair_rate": 0,
                "high_pair_rate": 0,
            },
            "latest_draw": None,
            "period_range": 0,
        }
