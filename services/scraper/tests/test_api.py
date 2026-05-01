from fastapi.testclient import TestClient

from app.main import app


def test_health_check_reports_healthy_status():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_scrape_endpoint_returns_items(monkeypatch):
    def fake_scrape_jobs(site, query, location=None, limit=10):
        return [
            {
                "title": query,
                "company": "Example Co",
                "location": location,
                "url": "https://example.com/job",
                "posted_date": "",
                "source": site,
            }
        ][:limit]

    monkeypatch.setattr("app.main.scrape_jobs", fake_scrape_jobs)
    client = TestClient(app)

    response = client.post(
        "/scrape",
        json={
            "site": "linkedin",
            "query": "Python Developer",
            "location": "London",
            "limit": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "items": [
            {
                "title": "Python Developer",
                "company": "Example Co",
                "location": "London",
                "url": "https://example.com/job",
                "posted_date": "",
                "source": "linkedin",
            }
        ],
        "error": None,
    }
