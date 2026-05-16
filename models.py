from pydantic import BaseModel
from typing import Optional

class Account(BaseModel):
    id: int
    name: str
    auto_swap_enabled: bool

class SwapHistory(BaseModel):
    direction: str
    input_amount: str
    output_amount: str
    status: str
    executed_at: str

class GasThreshold(BaseModel):
    threshold: Optional[float]
