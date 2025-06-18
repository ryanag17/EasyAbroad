from pydantic import BaseModel
from typing import List

class ConsultantAvailabilityOut(BaseModel):
    days_of_week: List[int]
    start_time: str
    end_time: str