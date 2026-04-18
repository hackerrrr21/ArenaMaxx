from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class SeatUpdateSchema(BaseModel):
    block: str = Field(..., min_length=1, max_length=20)
    row: str = Field(..., min_length=1, max_length=5)
    seat_number: int = Field(..., gt=0)
    status: str = Field(..., pattern="^(available|booked|unavailable)$")

class ConcessionOrderSchema(BaseModel):
    items: str = Field(..., min_length=3)
    user_id: Optional[str] = "anonymous"

class WashroomQueueSchema(BaseModel):
    block: str
    user_id: str

class ChatMessageSchema(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    user_id: Optional[str] = "guest"

    @field_validator('message')
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        # Simple mitigation for prompt injection or malicious scripts
        import bleach
        return bleach.clean(v)
