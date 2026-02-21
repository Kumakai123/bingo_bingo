from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class NumberResult(BaseModel):
    number: str
    score: float
    rank: int


class BasicPredictionResponse(BaseModel):
    prediction_type: str
    period_range: int
    method: str
    predictions: List[NumberResult]


class HighLowResponse(BaseModel):
    prediction: Optional[str] = None
    confidence: float = 0
    reason: str = ""
    statistics: Dict[str, Any] = {}
    period_range: int = 0


class OddEvenResponse(BaseModel):
    prediction: Optional[str] = None
    confidence: float = 0
    reason: str = ""
    statistics: Dict[str, Any] = {}
    period_range: int = 0
