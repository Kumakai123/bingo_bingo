from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult


class OddEvenAnalyzer:
    """猜單雙趨勢分析（邏輯與 HighLowAnalyzer 對稱）"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(self, period_range: int = 30) -> Dict:
        draws = (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(period_range)
            .all()
        )
        if not draws:
            return {"prediction": None, "statistics": {}, "period_range": 0}

        results = [d.odd_even_result for d in draws]

        odd_n = results.count("單")
        even_n = results.count("雙")
        tie_n = results.count("－")
        total = odd_n + even_n

        streak = self._calc_streak(results)
        avg_odd = sum(d.odd_count or 0 for d in draws) / len(draws)
        prediction = self._predict(odd_n, even_n, total, streak)

        return {
            "prediction": prediction["result"],
            "confidence": prediction["confidence"],
            "reason": prediction["reason"],
            "statistics": {
                "odd_count": odd_n,
                "even_count": even_n,
                "tie_count": tie_n,
                "odd_pct": round(odd_n / total * 100, 1) if total else 0,
                "even_pct": round(even_n / total * 100, 1) if total else 0,
                "current_streak": streak,
                "avg_odd_numbers": round(avg_odd, 1),
            },
            "period_range": len(draws),
        }

    def _calc_streak(self, results: List[str]) -> Dict:
        streak_type, streak_count = None, 0
        for r in results:
            if r == "－":
                continue
            if streak_type is None:
                streak_type, streak_count = r, 1
            elif r == streak_type:
                streak_count += 1
            else:
                break
        return {"type": streak_type, "count": streak_count}

    def _predict(self, odd_n, even_n, total, streak) -> Dict:
        if streak["count"] >= 3 and streak["type"] in ("單", "雙"):
            opposite = "雙" if streak["type"] == "單" else "單"
            confidence = min(0.60 + (streak["count"] - 3) * 0.05, 0.80)
            return {
                "result": opposite,
                "confidence": round(confidence, 2),
                "reason": f"連續 {streak['count']} 期開{streak['type']}，預測反轉",
            }
        if total > 0:
            odd_ratio = odd_n / total
            if odd_ratio > 0.70:
                return {
                    "result": "雙",
                    "confidence": 0.65,
                    "reason": f"單號比例偏高 ({odd_ratio:.0%})",
                }
            if odd_ratio < 0.30:
                return {
                    "result": "單",
                    "confidence": 0.65,
                    "reason": f"雙號比例偏高 ({1 - odd_ratio:.0%})",
                }
        result = "單" if odd_n >= even_n else "雙"
        return {"result": result, "confidence": 0.52, "reason": "根據歷史多數"}

