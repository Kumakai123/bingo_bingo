from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from app.database import Base


class SimulatedBet(Base):
    __tablename__ = "simulated_bets"

    id = Column(Integer, primary_key=True, index=True)
    bet_type = Column(String(20), nullable=False)  # basic / super / high_low / odd_even
    star_level = Column(Integer, nullable=True)  # 1-10, basic only
    selected_numbers = Column(Text, nullable=True)  # "07,11,33" for basic/super
    selected_option = Column(String(10), nullable=True)  # "大"/"小"/"單"/"雙"
    bet_amount = Column(Integer, default=25)
    multiplier = Column(Integer, default=1)  # 1-50

    target_draw_term = Column(String(20), nullable=True, index=True)

    status = Column(String(20), default="pending", nullable=False)  # pending / won / lost
    settled_draw_term = Column(String(20), nullable=True)
    matched_count = Column(Integer, nullable=True)
    matched_numbers = Column(Text, nullable=True)
    prize_amount = Column(Integer, default=0)
    net_profit = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)

    @property
    def total_cost(self) -> int:
        return self.bet_amount * self.multiplier
