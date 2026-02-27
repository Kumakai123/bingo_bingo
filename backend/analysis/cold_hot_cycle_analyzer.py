from collections import Counter
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult

ALL_NUMBERS = [f"{i:02d}" for i in range(1, 81)]


class ColdHotCycleAnalyzer:
    """冷熱週期分析：追蹤每個號碼的出現間隔、連莊、冷熱狀態"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(
        self,
        period_range: int = 100,
        recent_window: int = 10,
        top_n: int = 10,
    ) -> Dict:
        draws = self._fetch_draws(period_range)
        if not draws:
            return self._empty_result()

        total = len(draws)
        actual_recent = min(recent_window, total)

        number_stats = self._build_number_stats(draws, total)
        recent_hot = self._get_recent_hot(draws[:actual_recent], top_n)
        coldest = self._get_coldest(number_stats, top_n)
        streak_numbers = self._get_streak_numbers(draws)

        return {
            "number_stats": number_stats,
            "hot_numbers": recent_hot,
            "cold_numbers": coldest,
            "streak_numbers": streak_numbers,
            "period_range": total,
            "recent_window": actual_recent,
        }

    def _build_number_stats(self, draws, total: int) -> Dict:
        last_seen: Dict[str, int] = {}
        gaps: Dict[str, List[int]] = {n: [] for n in ALL_NUMBERS}

        for idx, draw in enumerate(draws):
            nums = set(draw.get_numbers_list())
            for n in ALL_NUMBERS:
                if n in nums:
                    if n in last_seen:
                        gap = idx - last_seen[n]
                        gaps[n].append(gap)
                    last_seen[n] = idx

        stats = {}
        for n in ALL_NUMBERS:
            current_gap = last_seen.get(n, total)
            all_gaps = gaps[n]
            appear_count = len(all_gaps) + (1 if n in last_seen else 0)
            avg_interval = round(total / appear_count, 2) if appear_count > 0 else total
            max_gap = max(all_gaps) if all_gaps else current_gap

            if appear_count == 0:
                phase = "inactive"
            elif current_gap <= avg_interval * 0.5:
                phase = "hot"
            elif current_gap >= avg_interval * 1.5:
                phase = "cold"
            else:
                phase = "normal"

            stats[n] = {
                "appear_count": appear_count,
                "avg_interval": avg_interval,
                "max_gap": max_gap,
                "current_gap": current_gap,
                "phase": phase,
            }

        return stats

    def _get_recent_hot(self, recent_draws, top_n: int) -> List[Dict]:
        counter = Counter()
        for draw in recent_draws:
            counter.update(draw.get_numbers_list())

        return [
            {"number": num, "recent_count": cnt}
            for num, cnt in counter.most_common(top_n)
        ]

    def _get_coldest(self, number_stats: Dict, top_n: int) -> List[Dict]:
        sorted_by_gap = sorted(
            number_stats.items(),
            key=lambda x: x[1]["current_gap"],
            reverse=True,
        )
        return [
            {
                "number": n,
                "current_gap": s["current_gap"],
                "avg_interval": s["avg_interval"],
            }
            for n, s in sorted_by_gap[:top_n]
        ]

    def _get_streak_numbers(self, draws) -> List[Dict]:
        """找出連續 N 期都出現的號碼（連莊號碼）"""
        if not draws:
            return []

        latest_nums = set(draws[0].get_numbers_list())
        streaks = {n: 1 for n in latest_nums}

        for draw in draws[1:]:
            nums = set(draw.get_numbers_list())
            still_active = False
            for n in list(streaks.keys()):
                if n in nums:
                    streaks[n] += 1
                    still_active = True
                else:
                    pass
            if not still_active:
                break

        streak_list = [
            {"number": n, "streak": s}
            for n, s in streaks.items()
            if s >= 2
        ]
        return sorted(streak_list, key=lambda x: x["streak"], reverse=True)

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(limit)
            .all()
        )

    def _empty_result(self) -> Dict:
        return {
            "number_stats": {},
            "hot_numbers": [],
            "cold_numbers": [],
            "streak_numbers": [],
            "period_range": 0,
            "recent_window": 0,
        }
