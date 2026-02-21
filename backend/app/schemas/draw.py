from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DrawResponse(BaseModel):
    draw_term: str
    draw_datetime: datetime
    numbers_sorted: List[str]
    super_number: str
    high_low_result: Optional[str] = None
    odd_even_result: Optional[str] = None

    model_config = {"from_attributes": True}
