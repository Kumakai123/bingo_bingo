from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult

STREAK_REVERSAL_THRESHOLD = 3
STREAK_BASE_CONFIDENCE = 0.60
STREAK_STEP = 0.05
STREAK_MAX_CONFIDENCE = 0.80
RATIO_IMBALANCE_THRESHOLD = 0.70
RATIO_CONFIDENCE = 0.65
MEAN_REVERSION_THRESHOLD = 1.5
MEAN_REVERSION_BASE_CONFIDENCE = 0.58
MAJORITY_CONFIDENCE = 0.52
THEORETICAL_AVG = 10.0


class TrendAnalyzer(ABC):
    """趨勢分析基底類別：連莊反轉 > 均值回歸 > 比例失衡 > 多數優先"""

    def __init__(self, db_session: Session):
        self.db = db_session

    @abstractmethod
    def _get_result(self, draw: DrawResult) -> str:
        """取得該期的結果字串（大/小、單/雙）"""

    @abstractmethod
    def _get_count(self, draw: DrawResult) -> float:
        """取得該期的正向計數值（high_count 或 odd_count）"""

    @abstractmethod
    def _labels(self) -> Tuple[str, str, str]:
        """回傳 (positive_label, negative_label, tie_label)"""

    @abstractmethod
    def _stat_keys(self) -> Tuple[str, str, str]:
        """回傳統計字典的 key 前綴 (pos_key, neg_key, avg_key)，保持 API 向後相容"""

    def analyze(self, period_range: int = 30) -> Dict:
        draws = self._fetch_draws(period_range)
        if not draws:
            return {"prediction": None, "statistics": {}, "period_range": 0}

        pos_label, neg_label, tie_label = self._labels()
        pos_key, neg_key, avg_key = self._stat_keys()
        results = [self._get_result(d) for d in draws]

        pos_n = results.count(pos_label)
        neg_n = results.count(neg_label)
        tie_n = results.count(tie_label)
        total = pos_n + neg_n

        streak = self._calc_streak(results, tie_label)
        avg_count = sum(self._get_count(d) for d in draws) / len(draws)
        prediction = self._predict(pos_n, neg_n, total, streak, avg_count)

        return {
            "prediction": prediction["result"],
            "confidence": prediction["confidence"],
            "reason": prediction["reason"],
            "statistics": {
                f"{pos_key}_count": pos_n,
                f"{neg_key}_count": neg_n,
                "tie_count": tie_n,
                f"{pos_key}_pct": round(pos_n / total * 100, 1) if total else 0,
                f"{neg_key}_pct": round(neg_n / total * 100, 1) if total else 0,
                "current_streak": streak,
                f"avg_{avg_key}_numbers": round(avg_count, 1),
            },
            "period_range": len(draws),
        }

    def _calc_streak(self, results: List[str], tie_label: str) -> Dict:
        streak_type = None
        streak_count = 0

        for r in results:
            if r == tie_label:
                if streak_type is not None:
                    break
                continue
            if streak_type is None:
                streak_type = r
                streak_count = 1
            elif r == streak_type:
                streak_count += 1
            else:
                break

        return {"type": streak_type, "count": streak_count}

    def _predict(
        self, pos_n: int, neg_n: int, total: int, streak: Dict, avg_count: float
    ) -> Dict:
        pos_label, neg_label, _ = self._labels()

        if streak["count"] >= STREAK_REVERSAL_THRESHOLD and streak["type"] in (
            pos_label, neg_label,
        ):
            opposite = neg_label if streak["type"] == pos_label else pos_label
            confidence = min(
                STREAK_BASE_CONFIDENCE + (streak["count"] - STREAK_REVERSAL_THRESHOLD) * STREAK_STEP,
                STREAK_MAX_CONFIDENCE,
            )
            return {
                "result": opposite,
                "confidence": round(confidence, 2),
                "reason": f"連續 {streak['count']} 期開{streak['type']}，預測反轉",
            }

        deviation = abs(avg_count - THEORETICAL_AVG)
        if deviation >= MEAN_REVERSION_THRESHOLD:
            predicted = neg_label if avg_count > THEORETICAL_AVG else pos_label
            confidence = min(
                MEAN_REVERSION_BASE_CONFIDENCE + deviation * 0.02,
                0.72,
            )
            direction = "偏高" if avg_count > THEORETICAL_AVG else "偏低"
            return {
                "result": predicted,
                "confidence": round(confidence, 2),
                "reason": f"平均{pos_label}數 {avg_count:.1f} {direction}（理論值 {THEORETICAL_AVG}），均值回歸",
            }

        if total > 0:
            pos_ratio = pos_n / total
            if pos_ratio > RATIO_IMBALANCE_THRESHOLD:
                return {
                    "result": neg_label,
                    "confidence": RATIO_CONFIDENCE,
                    "reason": f"{pos_label}比例偏高 ({pos_ratio:.0%})",
                }
            if pos_ratio < (1 - RATIO_IMBALANCE_THRESHOLD):
                return {
                    "result": pos_label,
                    "confidence": RATIO_CONFIDENCE,
                    "reason": f"{neg_label}比例偏高 ({1 - pos_ratio:.0%})",
                }

        result = pos_label if pos_n >= neg_n else neg_label
        return {
            "result": result,
            "confidence": MAJORITY_CONFIDENCE,
            "reason": "根據歷史多數",
        }

    def _fetch_draws(self, limit: int):
        return (
            self.db.query(DrawResult)
            .order_by(DrawResult.draw_term.desc())
            .limit(limit)
            .all()
        )
