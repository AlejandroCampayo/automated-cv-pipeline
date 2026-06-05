"""Moovijob source — wraps the existing Playwright scraper."""
from ..moovijob_scraper import scrape_moovijob_sync


def fetch(roles=None, locations=None):
    """Scrape Moovijob Luxembourg (IT + Data/AI fields). Returns normalized jobs."""
    return scrape_moovijob_sync(fetch_descriptions=True)
