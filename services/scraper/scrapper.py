from app.scraper import scrape_jobs, scrape_linkedin_jobs

__all__ = ["scrape_jobs", "scrape_linkedin_jobs"]


if __name__ == "__main__":
    import json

    results = scrape_jobs("linkedin", "Graduate Technology", "United Kingdom", 10)
    print(json.dumps(results, indent=2))
