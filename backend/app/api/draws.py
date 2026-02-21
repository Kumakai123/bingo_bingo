from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.draw_result import DrawResult

router = APIRouter()


@router.get("/latest")
def get_latest_draws(
    limit: int = Query(20, ge=1, le=100, description="筆數"),
    db: Session = Depends(get_db),
):
    """取得最新開獎紀錄"""
    draws = (
        db.query(DrawResult)
        .order_by(DrawResult.draw_term.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "draw_term": d.draw_term,
            "draw_datetime": d.draw_datetime,
            "numbers_sorted": d.numbers_sorted.split(","),
            "super_number": d.super_number,
            "high_low_result": d.high_low_result,
            "odd_even_result": d.odd_even_result,
        }
        for d in draws
    ]


@router.get("/{draw_term}")
def get_draw_by_term(draw_term: str, db: Session = Depends(get_db)):
    """取得特定期號資料"""
    draw = db.query(DrawResult).filter_by(draw_term=draw_term).first()
    if not draw:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="期號不存在")
    return {
        "draw_term": draw.draw_term,
        "draw_datetime": draw.draw_datetime,
        "numbers_sorted": draw.numbers_sorted.split(","),
        "super_number": draw.super_number,
        "high_low_result": draw.high_low_result,
        "odd_even_result": draw.odd_even_result,
    }
