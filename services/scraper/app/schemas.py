from typing import Optional

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    """Request schema for n8n to call the scraper API."""

    site: str = Field(..., examples=["linkedin"])
    query: str = Field(..., examples=["Python Developer"])
    location: Optional[str] = Field(default=None, examples=["London"])
    limit: int = Field(default=10, ge=1, le=100)


class ScrapeResponse(BaseModel):
    """Response schema with an items array that n8n can map directly."""

    success: bool
    items: list[dict]
    error: Optional[str] = None
