"""Common Pydantic models for API envelopes and pagination."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page index (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list envelope."""

    items: List[T]
    total: int = Field(ge=0, description="Total matching items count")
    page: int = Field(ge=1, description="Current page index")
    page_size: int = Field(ge=1, description="Number of items per page")
    total_pages: int = Field(ge=0, description="Total number of pages")


class StatusResponse(BaseModel):
    """Simple status/confirmation response."""

    status: str = "ok"
    message: Optional[str] = None
