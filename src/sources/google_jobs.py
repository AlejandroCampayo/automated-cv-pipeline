"""Google Jobs via SerpAPI — requires SERPAPI_KEY.

Free tier: ~100 searches/month. We spend one search per (role x location) pair,
so keep the role/location lists short. Docs: https://serpapi.com/google-jobs-api
"""
import os
import requests

API_URL = "https://serpapi.com/search.json"
TIMEOUT = 25


def fetch(roles=None, locations=None):
    """Query Google Jobs for each role/location pair and normalize results."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []

    roles = roles or ["machine learning engineer"]
    locations = locations or ["Luxembourg"]

    jobs = []
    seen = set()
    # Cap the number of API calls to protect the free quota.
    pairs = [(r, l) for l in locations for r in roles][:6]

    for role, location in pairs:
        params = {
            "engine": "google_jobs",
            "q": role,
            "location": location,
            "api_key": api_key,
        }
        resp = requests.get(API_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        for item in resp.json().get("jobs_results", []):
            url = ""
            for opt in item.get("apply_options", []) or []:
                if opt.get("link"):
                    url = opt["link"]
                    break
            url = url or item.get("share_link", "")
            if url in seen:
                continue
            seen.add(url)
            jobs.append({
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "location": item.get("location", location),
                "url": url,
                "posted_date": (item.get("detected_extensions", {}) or {}).get("posted_at", ""),
                "description": (item.get("description", "") or "")[:2000],
                "salary": (item.get("detected_extensions", {}) or {}).get("salary"),
                "source": "GoogleJobs",
            })
    return jobs
