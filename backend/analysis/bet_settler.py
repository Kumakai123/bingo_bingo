"""
兌獎引擎：比對投注與開獎結果，計算獎金。
"""
import logging
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.models.draw_result import DrawResult
from app.models.simulated_bet import SimulatedBet
from analysis.payout_table import calculate_prize

logger = logging.getLogger(__name__)


def settle_bet(bet: SimulatedBet, draw: DrawResult) -> SimulatedBet:
    """
    用一期開獎結果結算單筆投注。
    直接修改 bet 物件的欄位（呼叫端負責 commit）。
    """
    draw_numbers = set(draw.get_numbers_list())
    cost = bet.bet_amount * bet.multiplier

    if bet.bet_type == "basic":
        selected = set(bet.selected_numbers.split(",")) if bet.selected_numbers else set()
        matched = sorted(selected & draw_numbers)
        matched_count = len(matched)

        prize = calculate_prize(
            bet_type="basic",
            matched_count=matched_count,
            bet_amount=cost,
            star_level=bet.star_level,
        )
        bet.matched_count = matched_count
        bet.matched_numbers = ",".join(matched) if matched else None

    elif bet.bet_type == "super":
        selected = set(bet.selected_numbers.split(",")) if bet.selected_numbers else set()
        won = draw.super_number in selected
        bet.matched_count = 1 if won else 0
        bet.matched_numbers = draw.super_number if won else None

        prize = calculate_prize(
            bet_type="super",
            matched_count=bet.matched_count,
            bet_amount=cost,
            won=won,
        )

    elif bet.bet_type == "high_low":
        actual = draw.high_low_result  # "大" / "小" / "－"
        won = actual == bet.selected_option
        bet.matched_count = 1 if won else 0
        bet.matched_numbers = None

        prize = calculate_prize(
            bet_type="high_low",
            matched_count=0,
            bet_amount=cost,
            won=won,
        )

    elif bet.bet_type == "odd_even":
        actual = draw.odd_even_result  # "單" / "雙" / "－"
        won = actual == bet.selected_option
        bet.matched_count = 1 if won else 0
        bet.matched_numbers = None

        prize = calculate_prize(
            bet_type="odd_even",
            matched_count=0,
            bet_amount=cost,
            won=won,
        )

    else:
        prize = 0

    bet.prize_amount = prize
    bet.net_profit = prize - cost
    bet.status = "won" if prize > 0 else "lost"
    bet.settled_draw_term = draw.draw_term
    bet.settled_at = datetime.utcnow()

    return bet


def auto_settle_all(db: Session, draw: DrawResult) -> int:
    """
    結算所有目標期號 == 此期的 pending 投注。
    兼容舊資料：target_draw_term 為 NULL 時 fallback 用 created_at 比對。
    """
    from sqlalchemy import or_

    pending_bets: List[SimulatedBet] = (
        db.query(SimulatedBet)
        .filter(
            SimulatedBet.status == "pending",
            or_(
                SimulatedBet.target_draw_term == draw.draw_term,
                (SimulatedBet.target_draw_term.is_(None))
                & (SimulatedBet.created_at < draw.draw_datetime),
            ),
        )
        .all()
    )

    if not pending_bets:
        return 0

    settled = 0
    for bet in pending_bets:
        try:
            settle_bet(bet, draw)
            settled += 1
        except Exception:
            logger.exception("Failed to settle bet id=%s", bet.id)

    db.commit()
    logger.info(
        "Auto-settled %d/%d bets against draw %s",
        settled,
        len(pending_bets),
        draw.draw_term,
    )
    return settled
