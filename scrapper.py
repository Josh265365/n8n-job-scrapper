"""
LinkedIn Job Scraper using Playwright and BeautifulSoup.
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import Optional


async def scrape_linkedin_jobs(
    query: str,
    location: Optional[str] = None,
    limit: int = 10
) -> list[dict]:
    """
    Scrape job listings from LinkedIn.

    Args:
        query: Job title/keywords
        location: Optional location filter
        limit: Max jobs to return

    Returns:
        List of job dicts with keys: title, company, location, url, posted_date, source
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Build search URL
        url = f"https://www.linkedin.com/jobs/search?keywords={query.replace(' ', '%20')}"
        if location:
            url += f"&location={location.replace(' ', '%20')}"

        await page.goto(url, wait_until="domcontentloaded")

        # Scroll to trigger lazy loading
        for _ in range(5):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)

        # Get page content and parse with BeautifulSoup
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        jobs = []
        job_cards = soup.find_all('div', class_='base-card')

        for card in job_cards[:limit]:
            try:
                title_tag = card.find('h3', class_='base-search-card__title')
                company_tag = card.find('h4', class_='base-search-card__subtitle')
                location_tag = card.find('span', class_='job-search-card__location')
                link_tag = card.find('a', class_='base-card__full-link')
                date_tag = card.find('time', class_='job-search-card__listdate')

                jobs.append({
                    'title': title_tag.text.strip() if title_tag else "",
                    'company': company_tag.text.strip() if company_tag else "",
                    'location': location_tag.text.strip() if location_tag else "",
                    'url': link_tag['href'] if link_tag else "",
                    'posted_date': date_tag.text.strip() if date_tag else "",
                    'source': 'linkedin'
                })
            except Exception:
                continue

        await browser.close()
        return jobs


def scrape_jobs(
    site: str,
    query: str,
    location: Optional[str] = None,
    limit: int = 10
) -> list[dict]:
    """
    Synchronous wrapper for async scraper.
    FastAPI runs this in a threadpool.
    """
    if site.lower() != "linkedin":
        raise ValueError(f"Unsupported site: {site}. Only 'linkedin' is supported.")

    return asyncio.run(scrape_linkedin_jobs(query, location, limit))


# For quick local testing
if __name__ == "__main__":
    results = scrape_jobs("linkedin", "Graduate Technology", "United Kingdom", 10)
    import json
    print(json.dumps(results, indent=2))
