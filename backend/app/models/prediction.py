from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_type = Column(String(20), nullable=False)
    period_range = Column(Integer, nullable=False)
    predicted_numbers = Column(Text)  # JSON string
    predicted_result = Column(String(10))
    result_probability = Column(Float)
    confidence_scores = Column(Text)  # JSON string
    based_on_latest_term = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
