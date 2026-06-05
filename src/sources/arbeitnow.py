"""Arbeitnow job board — free public API, no key required.

Good coverage of EU + remote tech roles. Docs: https://www.arbeitnow.com/api
"""
import re
import requests

API_URL = "https://www.arbeitnow.com/api/job-board-api"
TIMEOUT = 20


def _strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch(roles=None, locations=None):
    """Fetch one page of the Arbeitnow board and normalize it."""
    resp = requests.get(API_URL, timeout=TIMEOUT, headers={"User-Agent": "job-bot"})
    resp.raise_for_status()
    data = resp.json().get("data", [])

    jobs = []
    for item in data:
        location = item.get("location", "")
        if item.get("remote"):
            location = (location + " (Remote)").strip()
        jobs.append({
            "title": item.get("title", ""),
            "company": item.get("company_name", ""),
            "location": location or "Europe",
            "url": item.get("url", ""),
            "posted_date": str(item.get("created_at", "")),
            "description": _strip_html(item.get("description", ""))[:2000],
            "salary": None,
            "source": "Arbeitnow",
        })
    return jobs
