from fastapi import FastAPI, HTTPException

from app.config import settings
from app.schemas import ScrapeRequest, ScrapeResponse
from app.scraper import scrape_jobs

app = FastAPI(
    title="Job Scraper API",
    description="HTTP API used by n8n workflows to scrape job listings.",
    version="0.1.0",
)


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_endpoint(request: ScrapeRequest):
    """
    n8n HTTP Request nodes call this endpoint and receive mappable JSON items.
    """
    try:
        jobs = scrape_jobs(
            site=request.site,
            query=request.query,
            location=request.location,
            limit=request.limit,
        )
        return ScrapeResponse(success=True, items=jobs, error=None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
async def health_check():
    """Health endpoint for Docker and n8n checks."""
    return {"status": "healthy"}


def run():
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
