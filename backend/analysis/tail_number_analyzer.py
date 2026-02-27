from collections import Counter, defaultdict
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult

TAIL_GROUPS = {i: [f"{n:02d}" for n in range(1, 81) if n % 10 == i] for i in range(10)}
TAIL_GROUPS[0] = [f"{n:02d}" for n in range(10, 81, 10)]


class TailNumberAnalyzer:
    """尾號分析：按尾數分 10 組統計出現頻率與熱門尾號"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(self, period_range: int = 30, top_n: int = 3) -> Dict:
        draws = self._fetch_draws(period_range)
        if not draws:
            return self._empty_result()

        total = len(draws)
        tail_counts: Dict[int, int] = defaultdict(int)
        tail_per_draw: List[Dict[int, int]] = []
        high_tail_draws = 0

        for draw in draws:
            nums = draw.get_numbers_list()
            draw_tails: Dict[int, int] = defaultdict(int)
            for n in nums:
                tail = int(n) % 10
                tail_counts[tail] += 1
                draw_tails[tail] += 1

            tail_per_draw.append(dict(draw_tails))
            max_tail_count = max(draw_tails.values()) if draw_tails else 0
            if max_tail_count >= 5:
                high_tail_draws += 1

        tail_stats = {}
        for tail in range(10):
            count = tail_counts.get(tail, 0)
            avg_per_draw = round(count / total, 2)
            tail_stats[str(tail)] = {
                "total_count": count,
                "avg_per_draw": avg_per_draw,
                "members": TAIL_GROUPS.get(tail, []),
            }

        sorted_tails = sorted(
            tail_stats.items(),
            key=lambda x: x[1]["total_count"],
            reverse=True,
        )
        hot_tails = [
            {"tail": t, "total_count": s["total_count"], "avg_per_draw": s["avg_per_draw"]}
            for t, s in sorted_tails[:top_n]
        ]

        hot_tail_numbers = self._get_hot_numbers_in_tails(draws, hot_tails)

        return {
            "tail_stats": tail_stats,
            "hot_tails": hot_tails,
            "hot_tail_numbers": hot_tail_numbers,
            "high_tail_draw_rate": round(high_tail_draws / total * 100, 2),
            "period_range": total,
        }

    def _get_hot_numbers_in_tails(self, draws, hot_tails) -> List[Dict]:
        """找出熱門尾號組中頻率最高的具體號碼"""
        counter = Counter()
        for draw in draws:
            counter.update(draw.get_numbers_list())

        result = []
        for ht in hot_tails:
            tail = int(ht["tail"])
            members = TAIL_GROUPS.get(tail, [])
            member_freq = sorted(
                [(m, counter.get(m, 0)) for m in members],
                key=lambda x: x[1],
                reverse=True,
            )
            result.append({
                "tail": ht["tail"],
                "top_numbers": [
                    {"number": num, "count": cnt}
                    for num, cnt in member_freq[:5]
                ],
            })
        return result

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(limit)
            .all()
        )

    def _empty_result(self) -> Dict:
        return {
            "tail_stats": {},
            "hot_tails": [],
            "hot_tail_numbers": [],
            "high_tail_draw_rate": 0,
            "period_range": 0,
        }
