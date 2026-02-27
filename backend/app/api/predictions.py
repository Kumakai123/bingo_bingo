from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from analysis.basic_analyzer import BasicAnalyzer
from analysis.super_number_analyzer import SuperNumberAnalyzer
from analysis.high_low_analyzer import HighLowAnalyzer
from analysis.odd_even_analyzer import OddEvenAnalyzer
from analysis.co_occurrence_analyzer import CoOccurrenceAnalyzer
from analysis.tail_number_analyzer import TailNumberAnalyzer
from analysis.zone_distribution_analyzer import ZoneDistributionAnalyzer
from analysis.cold_hot_cycle_analyzer import ColdHotCycleAnalyzer
from analysis.consecutive_number_analyzer import ConsecutiveNumberAnalyzer
from analysis.smart_pick_engine import SmartPickEngine

router = APIRouter()


@router.get("/basic")
def get_basic_prediction(
    period_range: int = Query(30, ge=5, le=500),
    top_n: int = Query(10, ge=5, le=20),
    use_weighted: bool = Query(True),
    db: Session = Depends(get_db),
):
    result = BasicAnalyzer(db).analyze(period_range, top_n, use_weighted)
    return {
        "prediction_type": "basic",
        "period_range": result["period_range"],
        "method": result["method"],
        "predictions": [
            {"number": num, "score": score, "rank": i + 1}
            for i, (num, score) in enumerate(result["predictions"])
        ],
        "repeat_info": result.get("repeat_info"),
        "consecutive_hits": result.get("consecutive_hits"),
    }


@router.get("/basic/batch")
def get_basic_batch(
    period_ranges: List[int] = Query([5, 10, 20, 30, 50, 100]),
    top_n: int = Query(10, ge=5, le=20),
    use_weighted: bool = Query(True),
    db: Session = Depends(get_db),
):
    analyzer = BasicAnalyzer(db)
    results = analyzer.batch_analyze(period_ranges, top_n, use_weighted)
    return {
        str(p): {
            "predictions": [
                {"number": num, "score": score, "rank": i + 1}
                for i, (num, score) in enumerate(r["predictions"])
            ],
            "period_range": r["period_range"],
        }
        for p, r in results.items()
    }


@router.get("/super-number")
def get_super_prediction(
    period_range: int = Query(30, ge=5, le=500),
    top_n: int = Query(10, ge=5, le=20),
    db: Session = Depends(get_db),
):
    result = SuperNumberAnalyzer(db).analyze(period_range, top_n)
    return {
        "prediction_type": "super_number",
        "period_range": result["period_range"],
        "predictions": [
            {"number": num, "frequency": freq, "rank": i + 1}
            for i, (num, freq) in enumerate(result["predictions"])
        ],
    }


@router.get("/high-low")
def get_high_low_prediction(
    period_range: int = Query(30, ge=5, le=500),
    db: Session = Depends(get_db),
):
    return HighLowAnalyzer(db).analyze(period_range)


@router.get("/odd-even")
def get_odd_even_prediction(
    period_range: int = Query(30, ge=5, le=500),
    db: Session = Depends(get_db),
):
    return OddEvenAnalyzer(db).analyze(period_range)


@router.get("/co-occurrence")
def get_co_occurrence(
    period_range: int = Query(30, ge=5, le=500),
    top_n: int = Query(15, ge=5, le=30),
    target_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return CoOccurrenceAnalyzer(db).analyze(period_range, top_n, target_number)


@router.get("/tail-number")
def get_tail_number(
    period_range: int = Query(30, ge=5, le=500),
    top_n: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
):
    return TailNumberAnalyzer(db).analyze(period_range, top_n)


@router.get("/zone-distribution")
def get_zone_distribution(
    period_range: int = Query(30, ge=5, le=500),
    db: Session = Depends(get_db),
):
    return ZoneDistributionAnalyzer(db).analyze(period_range)


@router.get("/cold-hot-cycle")
def get_cold_hot_cycle(
    period_range: int = Query(100, ge=10, le=500),
    recent_window: int = Query(10, ge=5, le=50),
    top_n: int = Query(10, ge=5, le=20),
    db: Session = Depends(get_db),
):
    return ColdHotCycleAnalyzer(db).analyze(period_range, recent_window, top_n)


@router.get("/consecutive")
def get_consecutive(
    period_range: int = Query(30, ge=5, le=500),
    db: Session = Depends(get_db),
):
    return ConsecutiveNumberAnalyzer(db).analyze(period_range)


@router.get("/smart-pick")
def get_smart_pick(
    period_range: int = Query(30, ge=5, le=500),
    pick_count: int = Query(10, ge=3, le=20),
    star_level: int = Query(3, ge=1, le=5),
    db: Session = Depends(get_db),
):
    return SmartPickEngine(db).pick(period_range, pick_count, star_level)


@router.get("/all")
def get_all_predictions(
    period_range: int = Query(30, ge=5, le=500),
    db: Session = Depends(get_db),
):
    return {
        "basic": BasicAnalyzer(db).analyze(period_range),
        "super_number": SuperNumberAnalyzer(db).analyze(period_range),
        "high_low": HighLowAnalyzer(db).analyze(period_range),
        "odd_even": OddEvenAnalyzer(db).analyze(period_range),
        "co_occurrence": CoOccurrenceAnalyzer(db).analyze(period_range),
        "tail_number": TailNumberAnalyzer(db).analyze(period_range),
        "zone_distribution": ZoneDistributionAnalyzer(db).analyze(period_range),
        "cold_hot_cycle": ColdHotCycleAnalyzer(db).analyze(period_range),
        "consecutive": ConsecutiveNumberAnalyzer(db).analyze(period_range),
        "period_range": period_range,
    }
