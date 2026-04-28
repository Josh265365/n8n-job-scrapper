"""
FastAPI wrapper for job scraper.
n8n calls this via HTTP Request node and receives JSON back.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

# Load environment variables from .env
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    headless: bool = True
    browser: str = "chromium"
    request_delay_ms: int = 1000
    user_agent: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

# Import your scraper logic
from scrapper import scrape_jobs  # adjust import if needed

app = FastAPI(title="Job Scraper API")


class ScrapeRequest(BaseModel):
    """Request schema for n8n -> scraper API"""
    site: str  # "linkedin", "indeed", etc.
    query: str  # job search query
    location: Optional[str] = None
    limit: Optional[int] = 10


class ScrapeResponse(BaseModel):
    """Response schema - n8n expects items array"""
    success: bool
    items: list[dict]
    error: Optional[str] = None


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_endpoint(request: ScrapeRequest):
    """
    n8n HTTP Request node calls this endpoint.
    Returns jobs in n8n-compatible JSON format.
    """
    try:
        jobs = scrape_jobs(
            site=request.site,
            query=request.query,
            location=request.location,
            limit=request.limit
        )
        return ScrapeResponse(
            success=True,
            items=jobs,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health endpoint for n8n to verify service is up"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
