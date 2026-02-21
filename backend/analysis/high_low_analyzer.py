from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult


class HighLowAnalyzer:
    """猜大小趨勢分析：連續性反轉 > 比例失衡 > 多數優先"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def analyze(self, period_range: int = 30) -> Dict:
        draws = (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_datetime.desc())
            .limit(period_range)
            .all()
        )
        if not draws:
            return {"prediction": None, "statistics": {}, "period_range": 0}

        results = [d.high_low_result for d in draws]

        high_n = results.count("大")
        low_n = results.count("小")
        tie_n = results.count("－")
        total = high_n + low_n

        streak = self._calc_streak(results)
        avg_high = sum(d.high_count or 0 for d in draws) / len(draws)
        prediction = self._predict(high_n, low_n, total, streak)

        return {
            "prediction": prediction["result"],
            "confidence": prediction["confidence"],
            "reason": prediction["reason"],
            "statistics": {
                "high_count": high_n,
                "low_count": low_n,
                "tie_count": tie_n,
                "high_pct": round(high_n / total * 100, 1) if total else 0,
                "low_pct": round(low_n / total * 100, 1) if total else 0,
                "current_streak": streak,
                "avg_high_numbers": round(avg_high, 1),
            },
            "period_range": len(draws),
        }

    def _calc_streak(self, results: List[str]) -> Dict:
        streak_type = None
        streak_count = 0

        for r in results:
            if r == "－":
                continue
            if streak_type is None:
                streak_type = r
                streak_count = 1
            elif r == streak_type:
                streak_count += 1
            else:
                break

        return {"type": streak_type, "count": streak_count}

    def _predict(self, high_n: int, low_n: int, total: int, streak: Dict) -> Dict:
        # Strategy 1: streak reversal
        if streak["count"] >= 3 and streak["type"] in ("大", "小"):
            opposite = "小" if streak["type"] == "大" else "大"
            confidence = min(0.60 + (streak["count"] - 3) * 0.05, 0.80)
            return {
                "result": opposite,
                "confidence": round(confidence, 2),
                "reason": f"連續 {streak['count']} 期開{streak['type']}，預測反轉",
            }

        # Strategy 2: ratio imbalance
        if total > 0:
            high_ratio = high_n / total
            if high_ratio > 0.70:
                return {
                    "result": "小",
                    "confidence": 0.65,
                    "reason": f"大號比例偏高 ({high_ratio:.0%})",
                }
            if high_ratio < 0.30:
                return {
                    "result": "大",
                    "confidence": 0.65,
                    "reason": f"小號比例偏高 ({1 - high_ratio:.0%})",
                }

        # Strategy 3: majority
        result = "大" if high_n >= low_n else "小"
        return {
            "result": result,
            "confidence": 0.52,
            "reason": "根據歷史多數",
        }
