from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from datetime import datetime

from app.database import Base


class DrawResult(Base):
    __tablename__ = "draw_results"

    id = Column(Integer, primary_key=True, index=True)
    draw_term = Column(String(20), unique=True, nullable=False, index=True)
    draw_date = Column(Date, nullable=False)
    draw_datetime = Column(DateTime, nullable=False, index=True)

    numbers_sorted = Column(Text, nullable=False)
    numbers_sequence = Column(Text, nullable=False)
    super_number = Column(String(2), nullable=False)

    high_low_result = Column(String(2))
    high_count = Column(Integer)
    low_count = Column(Integer)

    odd_even_result = Column(String(2))
    odd_count = Column(Integer)
    even_count = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    def get_numbers_list(self) -> list[str]:
        """Return sorted numbers as a list."""
        return self.numbers_sorted.split(",")

    def get_sequence_list(self) -> list[str]:
        """Return draw-order numbers as a list."""
        return self.numbers_sequence.split(",")
