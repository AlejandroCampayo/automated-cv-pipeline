"""Remotive — free public API for remote jobs, no key required.

Docs: https://remotive.com/api/remote-jobs  (category=software-dev covers ML/data).
"""
import re
import requests

API_URL = "https://remotive.com/api/remote-jobs"
TIMEOUT = 20


def _strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch(roles=None, locations=None):
    """Fetch software/data remote jobs from Remotive and normalize them."""
    params = {"category": "software-dev", "limit": 50}
    resp = requests.get(API_URL, params=params, timeout=TIMEOUT,
                        headers={"User-Agent": "job-bot"})
    resp.raise_for_status()
    data = resp.json().get("jobs", [])

    jobs = []
    for item in data:
        jobs.append({
            "title": item.get("title", ""),
            "company": item.get("company_name", ""),
            "location": item.get("candidate_required_location", "Remote") or "Remote",
            "url": item.get("url", ""),
            "posted_date": str(item.get("publication_date", "")),
            "description": _strip_html(item.get("description", ""))[:2000],
            "salary": item.get("salary") or None,
            "source": "Remotive",
        })
    return jobs
