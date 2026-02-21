from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from analysis.basic_analyzer import BasicAnalyzer
from analysis.super_number_analyzer import SuperNumberAnalyzer
from analysis.high_low_analyzer import HighLowAnalyzer
from analysis.odd_even_analyzer import OddEvenAnalyzer

router = APIRouter()


@router.get("/basic")
def get_basic_prediction(
    period_range: int = Query(30, ge=10, le=200),
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
    }


@router.get("/basic/batch")
def get_basic_batch(
    period_ranges: List[int] = Query([10, 20, 30, 50, 100]),
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
    period_range: int = Query(30, ge=10, le=200),
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
    period_range: int = Query(30, ge=10, le=200),
    db: Session = Depends(get_db),
):
    return HighLowAnalyzer(db).analyze(period_range)


@router.get("/odd-even")
def get_odd_even_prediction(
    period_range: int = Query(30, ge=10, le=200),
    db: Session = Depends(get_db),
):
    return OddEvenAnalyzer(db).analyze(period_range)


@router.get("/all")
def get_all_predictions(
    period_range: int = Query(30, ge=10, le=200),
    db: Session = Depends(get_db),
):
    return {
        "basic": BasicAnalyzer(db).analyze(period_range),
        "super_number": SuperNumberAnalyzer(db).analyze(period_range),
        "high_low": HighLowAnalyzer(db).analyze(period_range),
        "odd_even": OddEvenAnalyzer(db).analyze(period_range),
        "period_range": period_range,
    }
