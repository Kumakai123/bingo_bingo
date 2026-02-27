import math
from collections import Counter
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from analysis.basic_analyzer import BasicAnalyzer
from analysis.cold_hot_cycle_analyzer import ColdHotCycleAnalyzer
from analysis.co_occurrence_analyzer import CoOccurrenceAnalyzer
from analysis.tail_number_analyzer import TailNumberAnalyzer
from analysis.zone_distribution_analyzer import ZoneDistributionAnalyzer, ZONES

ALL_NUMBERS = [f"{i:02d}" for i in range(1, 81)]

CONSECUTIVE_2_BONUS = 0.20
CONSECUTIVE_3_BONUS = 0.35
CO_OCCURRENCE_BONUS = 0.15
HOT_TAIL_BONUS = 0.10
COLD_REVERSION_BONUS = 0.10
ZONE_PENALTY = 0.15


class SmartPickEngine:
    """綜合推薦引擎：整合多個分析器，按攻略邏輯自動選號"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def pick(
        self,
        period_range: int = 30,
        pick_count: int = 10,
        star_level: int = 3,
    ) -> Dict:
        basic = BasicAnalyzer(self.db).analyze(period_range, top_n=20, use_weighted=True)
        cycle = ColdHotCycleAnalyzer(self.db).analyze(period_range=max(period_range, 50), recent_window=10)
        co_occ = CoOccurrenceAnalyzer(self.db).analyze(period_range, top_n=20)
        tail = TailNumberAnalyzer(self.db).analyze(period_range, top_n=3)
        zone = ZoneDistributionAnalyzer(self.db).analyze(period_range)

        if not basic["predictions"]:
            return self._empty_result()

        anchors = self._select_anchors(cycle)

        scores = self._build_base_scores(basic)
        self._apply_consecutive_bonus(scores, basic.get("consecutive_hits", []))
        self._apply_co_occurrence_bonus(scores, co_occ, anchors)
        self._apply_tail_bonus(scores, tail)
        self._apply_cold_reversion_bonus(scores, cycle)
        self._apply_zone_balance(scores, zone, pick_count)

        ranked = sorted(scores.items(), key=lambda x: x[1]["final_score"], reverse=True)

        picks = []
        for num, info in ranked[:pick_count]:
            picks.append({
                "number": num,
                "final_score": round(info["final_score"], 3),
                "base_score": round(info["base_score"], 3),
                "bonuses": info["bonuses"],
                "reasons": info["reasons"],
            })

        star_combos = self._generate_star_combos(picks, star_level)

        return {
            "picks": picks,
            "anchors": anchors,
            "star_combos": star_combos,
            "star_level": star_level,
            "period_range": basic["period_range"],
        }

    def _select_anchors(self, cycle_result: Dict) -> List[str]:
        """選定 1-2 隻主隻：從熱號和連莊號中取交集或 Top"""
        hot = {h["number"] for h in cycle_result.get("hot_numbers", [])[:5]}
        streak = {s["number"] for s in cycle_result.get("streak_numbers", [])[:5]}

        overlap = sorted(hot & streak)
        if len(overlap) >= 2:
            return overlap[:2]
        if overlap:
            candidates = sorted(hot - set(overlap))
            return overlap + candidates[:1]
        hot_list = [h["number"] for h in cycle_result.get("hot_numbers", [])[:2]]
        return hot_list

    def _build_base_scores(self, basic_result: Dict) -> Dict[str, Dict]:
        scores = {}
        max_score = max((s for _, s in basic_result["predictions"]), default=1.0)

        for num, score in basic_result["predictions"]:
            normalized = score / max_score if max_score else 0
            scores[num] = {
                "base_score": normalized,
                "final_score": normalized,
                "bonuses": [],
                "reasons": [],
            }

        for n in ALL_NUMBERS:
            if n not in scores:
                scores[n] = {
                    "base_score": 0.0,
                    "final_score": 0.0,
                    "bonuses": [],
                    "reasons": [],
                }

        return scores

    def _apply_consecutive_bonus(self, scores: Dict, consecutive_hits: List[Dict]):
        for hit in consecutive_hits:
            num = hit["number"]
            streak = hit["consecutive_draws"]
            if num not in scores:
                continue
            if streak >= 3:
                bonus = CONSECUTIVE_3_BONUS
                scores[num]["bonuses"].append(f"連開{streak}期 +{int(bonus*100)}%")
            elif streak >= 2:
                bonus = CONSECUTIVE_2_BONUS
                scores[num]["bonuses"].append(f"連開{streak}期 +{int(bonus*100)}%")
            else:
                continue
            scores[num]["final_score"] += scores[num]["base_score"] * bonus
            scores[num]["reasons"].append("consecutive")

    def _apply_co_occurrence_bonus(
        self, scores: Dict, co_occ_result: Dict, anchors: List[str]
    ):
        if not anchors:
            return

        partner_set = set()
        for pair_info in co_occ_result.get("top_pairs", []):
            pair = pair_info["pair"]
            for anchor in anchors:
                if anchor in pair:
                    partner = pair[0] if pair[1] == anchor else pair[1]
                    partner_set.add(partner)

        for partner in partner_set:
            if partner in scores:
                scores[partner]["final_score"] += (
                    scores[partner]["base_score"] * CO_OCCURRENCE_BONUS
                )
                scores[partner]["bonuses"].append(f"與主隻共現 +{int(CO_OCCURRENCE_BONUS*100)}%")
                scores[partner]["reasons"].append("co_occurrence")

    def _apply_tail_bonus(self, scores: Dict, tail_result: Dict):
        hot_tails = {int(ht["tail"]) for ht in tail_result.get("hot_tails", [])}
        for num in scores:
            tail = int(num) % 10
            if tail in hot_tails:
                scores[num]["final_score"] += scores[num]["base_score"] * HOT_TAIL_BONUS
                scores[num]["bonuses"].append(f"熱門尾號{tail} +{int(HOT_TAIL_BONUS*100)}%")
                scores[num]["reasons"].append("hot_tail")

    def _apply_cold_reversion_bonus(self, scores: Dict, cycle_result: Dict):
        stats = cycle_result.get("number_stats", {})
        for num, info in stats.items():
            if num not in scores:
                continue
            avg_interval = info.get("avg_interval", 0)
            current_gap = info.get("current_gap", 0)
            if avg_interval > 0 and current_gap >= avg_interval * 1.5:
                scores[num]["final_score"] += (
                    scores[num]["base_score"] * COLD_REVERSION_BONUS
                )
                scores[num]["bonuses"].append(f"冷號回歸 +{int(COLD_REVERSION_BONUS*100)}%")
                scores[num]["reasons"].append("cold_reversion")

    def _apply_zone_balance(self, scores: Dict, zone_result: Dict, pick_count: int):
        zone_stats = zone_result.get("zone_stats", {})
        biased_zones = set()
        for zone_name, stat in zone_stats.items():
            if abs(stat.get("deviation_pct", 0)) > 20:
                if stat["deviation_pct"] > 0:
                    biased_zones.add(zone_name)

        if not biased_zones:
            return

        for num in scores:
            n = int(num)
            zone = None
            for z, (lo, hi) in ZONES.items():
                if lo <= n <= hi:
                    zone = z
                    break
            if zone in biased_zones:
                scores[num]["final_score"] -= (
                    scores[num]["base_score"] * ZONE_PENALTY
                )
                scores[num]["bonuses"].append(f"區間{zone}過度集中 -{int(ZONE_PENALTY*100)}%")
                scores[num]["reasons"].append("zone_penalty")

    def _generate_star_combos(
        self, picks: List[Dict], star_level: int
    ) -> List[List[str]]:
        """根據推薦號碼產生 star_level 星的組合建議"""
        if len(picks) < star_level:
            return [sorted(p["number"] for p in picks)]

        from itertools import combinations as comb

        pick_nums = [p["number"] for p in picks[:min(8, len(picks))]]
        combos = list(comb(pick_nums, star_level))

        scored_combos = []
        pick_scores = {p["number"]: p["final_score"] for p in picks}
        for combo in combos:
            total_score = sum(pick_scores.get(n, 0) for n in combo)
            scored_combos.append((sorted(combo), total_score))

        scored_combos.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in scored_combos[:5]]

    def _empty_result(self) -> Dict:
        return {
            "picks": [],
            "anchors": [],
            "star_combos": [],
            "star_level": 3,
            "period_range": 0,
        }
