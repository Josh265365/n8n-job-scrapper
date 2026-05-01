"""
LinkedIn job scraper using Playwright and BeautifulSoup.
"""

import asyncio
from typing import Optional
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.config import settings


async def scrape_linkedin_jobs(
    query: str,
    location: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Scrape job listings from LinkedIn.

    Returns dictionaries with title, company, location, url, posted_date, and source.
    """
    params = {"keywords": query}
    if location:
        params["location"] = location

    url = f"https://www.linkedin.com/jobs/search?{urlencode(params)}"

    async with async_playwright() as p:
        browser_type = getattr(p, settings.browser)
        browser = await browser_type.launch(headless=settings.headless)
        page = await browser.new_page(user_agent=settings.user_agent)

        try:
            await page.goto(url, wait_until="domcontentloaded")

            for _ in range(5):
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(settings.request_delay_ms / 1000)

            content = await page.content()
        finally:
            await browser.close()

    soup = BeautifulSoup(content, "html.parser")
    job_cards = soup.find_all("div", class_="base-card")

    jobs = []
    for card in job_cards[:limit]:
        title_tag = card.find("h3", class_="base-search-card__title")
        company_tag = card.find("h4", class_="base-search-card__subtitle")
        location_tag = card.find("span", class_="job-search-card__location")
        link_tag = card.find("a", class_="base-card__full-link")
        date_tag = card.find("time", class_="job-search-card__listdate")

        jobs.append(
            {
                "title": title_tag.text.strip() if title_tag else "",
                "company": company_tag.text.strip() if company_tag else "",
                "location": location_tag.text.strip() if location_tag else "",
                "url": link_tag["href"] if link_tag else "",
                "posted_date": date_tag.text.strip() if date_tag else "",
                "source": "linkedin",
            }
        )

    return jobs


def scrape_jobs(
    site: str,
    query: str,
    location: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Synchronous wrapper for FastAPI's threadpool execution."""
    if site.lower() != "linkedin":
        raise ValueError(f"Unsupported site: {site}. Only 'linkedin' is supported.")

    return asyncio.run(scrape_linkedin_jobs(query, location, limit))
