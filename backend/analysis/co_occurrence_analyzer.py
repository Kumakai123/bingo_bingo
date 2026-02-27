from collections import Counter
from itertools import combinations
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult


class CoOccurrenceAnalyzer:
    """共現分析：統計兩兩號碼在同一期同時出現的頻率"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(
        self,
        period_range: int = 30,
        top_n: int = 15,
        target_number: Optional[str] = None,
    ) -> Dict:
        draws = self._fetch_draws(period_range)
        if not draws:
            return self._empty_result()

        total = len(draws)
        pair_counter = Counter()

        for draw in draws:
            nums = sorted(draw.get_numbers_list())
            for pair in combinations(nums, 2):
                pair_counter[pair] += 1

        top_pairs = [
            {
                "pair": list(pair),
                "count": count,
                "co_rate": round(count / total * 100, 2),
            }
            for pair, count in pair_counter.most_common(top_n)
        ]

        result = {
            "top_pairs": top_pairs,
            "period_range": total,
        }

        if target_number is not None:
            target = target_number.zfill(2)
            target_pairs = {
                k: v for k, v in pair_counter.items() if target in k
            }
            top_partners = sorted(
                target_pairs.items(), key=lambda x: x[1], reverse=True
            )[:5]
            result["target_number"] = target
            result["target_partners"] = [
                {
                    "partner": p[0] if p[1] != target else p[0],
                    "count": cnt,
                    "co_rate": round(cnt / total * 100, 2),
                }
                for p, cnt in top_partners
            ]
            result["target_partners"] = [
                {
                    "partner": pair[0] if pair[1] == target else pair[1],
                    "count": cnt,
                    "co_rate": round(cnt / total * 100, 2),
                }
                for pair, cnt in top_partners
            ]

        return result

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(limit)
            .all()
        )

    def _empty_result(self) -> Dict:
        return {"top_pairs": [], "period_range": 0}
