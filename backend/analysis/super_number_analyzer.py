from collections import Counter
from typing import Dict
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult


class SuperNumberAnalyzer:
    """超級號碼分析：統計哪個號碼最常作為第 20 個號碼"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(self, period_range: int = 30, top_n: int = 10) -> Dict:
        draws = (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(period_range)
            .all()
        )
        if not draws:
            return {"predictions": [], "all_stats": {}, "period_range": 0}

        super_numbers = [d.super_number for d in draws]
        counter = Counter(super_numbers)

        all_stats = {
            f"{i:02d}": counter.get(f"{i:02d}", 0) for i in range(1, 81)
        }

        top = sorted(counter.items(), key=lambda x: x[1], reverse=True)[
            :top_n
        ]

        return {
            "predictions": top,
            "all_stats": all_stats,
            "period_range": len(draws),
        }

