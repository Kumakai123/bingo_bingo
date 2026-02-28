from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config import settings
from app.database import get_db
from app.models.draw_result import DrawResult
from app.models.simulated_bet import SimulatedBet
from analysis.bet_settler import auto_settle_all

router = APIRouter()

VALID_BET_TYPES = {"basic", "super", "high_low", "odd_even"}
VALID_OPTIONS = {"大", "小", "單", "雙"}
DRAW_INTERVAL_MINUTES = 5


class PlaceBetRequest(BaseModel):
    bet_type: str
    star_level: Optional[int] = None
    selected_numbers: Optional[List[str]] = None
    selected_option: Optional[str] = None
    multiplier: int = 1
    bet_periods: int = 1

    @field_validator("bet_type")
    @classmethod
    def validate_bet_type(cls, v: str) -> str:
        if v not in VALID_BET_TYPES:
            raise ValueError(f"bet_type 必須是 {VALID_BET_TYPES} 之一")
        return v

    @field_validator("multiplier")
    @classmethod
    def validate_multiplier(cls, v: int) -> int:
        if not 1 <= v <= 50:
            raise ValueError("倍數必須在 1~50 之間")
        return v

    @field_validator("bet_periods")
    @classmethod
    def validate_bet_periods(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError("期數必須在 1~10 之間")
        return v


def _get_latest_draw_term(db: Session) -> int:
    latest = (
        db.query(DrawResult.draw_term)
        .order_by(DrawResult.draw_term.desc())
        .first()
    )
    if not latest:
        raise HTTPException(404, "尚無開獎資料，無法計算下一期")
    return int(latest[0])


def _calc_next_draw_time(latest_term: int, db: Session) -> dict:
    """Calculate next draw term and estimated draw time."""
    next_term = latest_term + 1

    latest_draw = (
        db.query(DrawResult)
        .filter(DrawResult.draw_term == str(latest_term))
        .first()
    )
    if latest_draw and latest_draw.draw_datetime:
        next_time = latest_draw.draw_datetime + timedelta(minutes=DRAW_INTERVAL_MINUTES)
    else:
        now = datetime.now()
        mins = now.minute
        next_min = mins + (DRAW_INTERVAL_MINUTES - mins % DRAW_INTERVAL_MINUTES)
        next_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_min)

    return {
        "next_draw_term": str(next_term),
        "estimated_time": next_time.strftime("%Y-%m-%d %H:%M"),
        "estimated_time_short": next_time.strftime("%H:%M"),
    }


@router.get("/next-draw")
def get_next_draw(db: Session = Depends(get_db)):
    """取得下一期期號與預計開獎時間"""
    latest_term = _get_latest_draw_term(db)
    return _calc_next_draw_time(latest_term, db)


@router.post("/bet")
def place_bet(req: PlaceBetRequest, db: Session = Depends(get_db)):
    """下注（支援多期）"""
    if req.bet_type == "basic":
        if req.star_level is None or not 1 <= req.star_level <= 10:
            raise HTTPException(400, "基本玩法需要 star_level (1-10)")
        if not req.selected_numbers or len(req.selected_numbers) != req.star_level:
            raise HTTPException(
                400, f"{req.star_level} 星需要選 {req.star_level} 個號碼"
            )
        _validate_numbers(req.selected_numbers)

    elif req.bet_type == "super":
        if not req.selected_numbers or len(req.selected_numbers) != 1:
            raise HTTPException(400, "超級獎號需要選 1 個號碼")
        _validate_numbers(req.selected_numbers)

    elif req.bet_type in ("high_low", "odd_even"):
        if not req.selected_option or req.selected_option not in VALID_OPTIONS:
            raise HTTPException(400, f"需要 selected_option: {VALID_OPTIONS}")

    latest_term = _get_latest_draw_term(db)
    numbers_str = ",".join(req.selected_numbers) if req.selected_numbers else None

    created_bets = []
    for i in range(req.bet_periods):
        target_term = str(latest_term + 1 + i)
        bet = SimulatedBet(
            bet_type=req.bet_type,
            star_level=req.star_level,
            selected_numbers=numbers_str,
            selected_option=req.selected_option,
            bet_amount=25,
            multiplier=req.multiplier,
            target_draw_term=target_term,
            status="pending",
        )
        db.add(bet)
        created_bets.append(bet)

    db.commit()
    for b in created_bets:
        db.refresh(b)

    return [_bet_to_dict(b) for b in created_bets]


@router.get("/bets")
def get_bets(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """取得投注歷史"""
    query = db.query(SimulatedBet).order_by(SimulatedBet.id.desc())
    if status:
        query = query.filter(SimulatedBet.status == status)
    total = query.count()
    bets = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "bets": [_bet_to_dict(b) for b in bets],
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """取得投注統計"""
    rows = db.query(SimulatedBet).filter(SimulatedBet.status != "pending").all()
    total_cost = sum(r.bet_amount * r.multiplier for r in rows)
    total_prize = sum(r.prize_amount for r in rows)
    total_bets = len(rows)
    wins = sum(1 for r in rows if r.status == "won")
    pending = db.query(func.count(SimulatedBet.id)).filter(
        SimulatedBet.status == "pending"
    ).scalar()

    return {
        "total_bets": total_bets,
        "wins": wins,
        "losses": total_bets - wins,
        "pending": pending or 0,
        "win_rate": round(wins / total_bets * 100, 1) if total_bets else 0,
        "total_cost": total_cost,
        "total_prize": total_prize,
        "net_profit": total_prize - total_cost,
    }


@router.post("/settle")
def manual_settle(db: Session = Depends(get_db)):
    """手動用最新一期開獎結算所有 pending 投注"""
    latest_draw = (
        db.query(DrawResult)
        .order_by(DrawResult.draw_term.desc())
        .first()
    )
    if not latest_draw:
        raise HTTPException(404, "尚無開獎資料")

    settled = auto_settle_all(db, latest_draw)
    return {"settled_count": settled, "draw_term": latest_draw.draw_term}


@router.delete("/bet/{bet_id}")
def cancel_bet(bet_id: int, db: Session = Depends(get_db)):
    """取消 pending 投注"""
    bet = db.query(SimulatedBet).filter(SimulatedBet.id == bet_id).first()
    if not bet:
        raise HTTPException(404, "投注不存在")
    if bet.status != "pending":
        raise HTTPException(400, "只能取消 pending 狀態的投注")
    db.delete(bet)
    db.commit()
    return {"ok": True, "id": bet_id}


def _validate_numbers(numbers: List[str]):
    for n in numbers:
        try:
            val = int(n)
        except ValueError:
            raise HTTPException(400, f"號碼格式錯誤: {n}")
        if not 1 <= val <= 80:
            raise HTTPException(400, f"號碼必須在 01-80 之間: {n}")


def _bet_to_dict(bet: SimulatedBet) -> dict:
    return {
        "id": bet.id,
        "bet_type": bet.bet_type,
        "star_level": bet.star_level,
        "selected_numbers": bet.selected_numbers.split(",") if bet.selected_numbers else None,
        "selected_option": bet.selected_option,
        "bet_amount": bet.bet_amount,
        "multiplier": bet.multiplier,
        "total_cost": bet.bet_amount * bet.multiplier,
        "target_draw_term": bet.target_draw_term,
        "status": bet.status,
        "settled_draw_term": bet.settled_draw_term,
        "matched_count": bet.matched_count,
        "matched_numbers": bet.matched_numbers.split(",") if bet.matched_numbers else None,
        "prize_amount": bet.prize_amount,
        "net_profit": bet.net_profit,
        "created_at": bet.created_at.isoformat() if bet.created_at else None,
        "settled_at": bet.settled_at.isoformat() if bet.settled_at else None,
    }
