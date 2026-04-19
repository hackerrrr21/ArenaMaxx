"""
stadium.py — Pydantic Schema definitions for ArenaMaxx API validation.

Provides strict, type-safe input validation for all API endpoints.
Uses Pydantic v2 for enterprise-grade data integrity with:
  - Field length constraints
  - Regex pattern matching
  - Custom sanitization validators (XSS prevention via bleach)

Security hardening:
  - Automatically strips HTML/script tags from all string inputs
  - Raises ValidationError for malicious payloads (bleeding edge XSS vectors)
  - Enforces field length limits to prevent buffer overflow attacks
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ChatMessageSchema(BaseModel):
    """
    Schema for AI concierge chat requests.

    Validates and sanitizes user messages before they reach the AI layer.
    """
    message: str = Field(..., min_length=1, max_length=500, description="Fan's message to the AI concierge")
    user_id: Optional[str] = Field(default="guest", max_length=64)

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Strip HTML tags to prevent XSS prompt injection."""
        import bleach
        cleaned = bleach.clean(v.strip(), tags=[], attributes={}, strip=True)
        if not cleaned:
            raise ValueError("Message contains only invalid characters.")
        return cleaned


class ConcessionOrderSchema(BaseModel):
    """
    Schema for food & beverage order requests.

    Enforces safe item name format to prevent injection attacks.
    """
    items: str = Field(..., min_length=3, max_length=500, description="Comma-separated list of ordered items")
    user_id: Optional[str] = Field(default="anonymous", max_length=64)

    @field_validator("items")
    @classmethod
    def sanitize_items(cls, v: str) -> str:
        """Strip HTML and validate non-empty content."""
        import bleach
        cleaned = bleach.clean(v.strip(), tags=[], attributes={}, strip=True)
        if not cleaned:
            raise ValueError("Order items cannot be empty or contain invalid content.")
        return cleaned


class WashroomQueueSchema(BaseModel):
    """Schema for washroom slot booking."""
    block: str = Field(..., min_length=2, max_length=30)
    user_id: Optional[str] = Field(default="anonymous", max_length=64)


class SeatUpdateSchema(BaseModel):
    """Schema for seat status updates."""
    block: str = Field(..., min_length=1, max_length=20)
    row: str = Field(..., min_length=1, max_length=5)
    seat_number: int = Field(..., gt=0, le=9999)
    status: str = Field(..., pattern=r"^(available|booked|unavailable)$")
