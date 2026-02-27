from collections import defaultdict
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult

ZONES = {
    "A": (1, 20),
    "B": (21, 40),
    "C": (41, 60),
    "D": (61, 80),
}
THEORETICAL_AVG = 5.0


class ZoneDistributionAnalyzer:
    """區間分布分析：將 1-80 分為四區，統計分布與區間搭配傾向"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(self, period_range: int = 30) -> Dict:
        draws = self._fetch_draws(period_range)
        if not draws:
            return self._empty_result()

        total = len(draws)
        zone_totals: Dict[str, int] = defaultdict(int)
        zone_per_draw: List[Dict[str, int]] = []
        zone_high_draws: Dict[str, List[Dict[str, float]]] = {
            z: [] for z in ZONES
        }

        for draw in draws:
            nums = [int(n) for n in draw.get_numbers_list()]
            draw_zones: Dict[str, int] = {}
            for zone_name, (lo, hi) in ZONES.items():
                count = sum(1 for n in nums if lo <= n <= hi)
                draw_zones[zone_name] = count
                zone_totals[zone_name] += count

            zone_per_draw.append(draw_zones)

            for zone_name in ZONES:
                if draw_zones[zone_name] >= 7:
                    others = {
                        z: draw_zones[z]
                        for z in ZONES
                        if z != zone_name
                    }
                    zone_high_draws[zone_name].append(others)

        zone_stats = {}
        for zone_name, (lo, hi) in ZONES.items():
            avg = round(zone_totals[zone_name] / total, 2)
            deviation = round((avg - THEORETICAL_AVG) / THEORETICAL_AVG * 100, 2)
            zone_stats[zone_name] = {
                "range": f"{lo}-{hi}",
                "total_count": zone_totals[zone_name],
                "avg_per_draw": avg,
                "theoretical_avg": THEORETICAL_AVG,
                "deviation_pct": deviation,
            }

        pairing_tendency = {}
        for zone_name in ZONES:
            high_list = zone_high_draws[zone_name]
            if high_list:
                avg_others = {}
                for other_zone in ZONES:
                    if other_zone == zone_name:
                        continue
                    avg_others[other_zone] = round(
                        sum(h[other_zone] for h in high_list) / len(high_list), 2
                    )
                pairing_tendency[zone_name] = {
                    "occurrences": len(high_list),
                    "avg_other_zones": avg_others,
                }

        most_extreme = None
        max_diff = 0
        for i, draw_zones in enumerate(zone_per_draw):
            diff = max(draw_zones.values()) - min(draw_zones.values())
            if diff > max_diff:
                max_diff = diff
                most_extreme = {
                    "draw_index": i,
                    "zones": draw_zones,
                    "diff": diff,
                    "draw_term": draws[i].draw_term,
                }

        return {
            "zone_stats": zone_stats,
            "pairing_tendency": pairing_tendency,
            "most_extreme_draw": most_extreme,
            "period_range": total,
        }

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(limit)
            .all()
        )

    def _empty_result(self) -> Dict:
        return {
            "zone_stats": {},
            "pairing_tendency": {},
            "most_extreme_draw": None,
            "period_range": 0,
        }
