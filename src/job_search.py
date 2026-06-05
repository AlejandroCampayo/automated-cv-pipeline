"""Moovijob scraper for Luxembourg jobs."""
from .moovijob_scraper import scrape_moovijob_sync


def get_test_jobs():
    """Return sample jobs for testing."""
    return [
        {
            "title": "Machine Learning Engineer",
            "company": "TechCorp Luxembourg",
            "location": "Luxembourg",
            "url": "https://example.com/ml-engineer-1",
            "posted_date": "2 days ago",
            "description": "We are looking for an experienced ML Engineer with 3+ years of Python and PyTorch experience. You will work on cutting-edge LLM applications.",
            "source": "Test",
        },
        {
            "title": "AI Research Engineer",
            "company": "StartupAI",
            "location": "Remote (EU)",
            "url": "https://example.com/ai-research-1",
            "posted_date": "1 day ago",
            "description": "Join our remote team to build agentic AI systems. Strong background in transformers and prompt engineering required.",
            "source": "Test",
        },
        {
            "title": "Data Scientist - Computer Vision",
            "company": "Vision Labs",
            "location": "Luxembourg",
            "url": "https://example.com/cv-ds-1",
            "posted_date": "Today",
            "description": "We need a Data Scientist with experience in computer vision and deep learning. Working with state-of-the-art CV models.",
            "source": "Test",
        },
    ]


def batch_search_jobs(roles=None, locations=None, limit=None, test_mode=False):
    """
    Aggregate job listings from every available source (see src/sources/).

    Args:
        roles: list of role keywords (drives keyword-based sources like Google Jobs)
        locations: list of locations (e.g. ["Luxembourg", "Remote"])
        limit: Max jobs to return (None = all)
        test_mode: If True, return sample jobs for testing

    Returns:
        Merged, de-duplicated list of job postings.
    """
    if test_mode:
        print("  Using TEST MODE with sample jobs")
        return get_test_jobs()

    print("  Searching all available sources...")
    from .sources import fetch_all
    jobs = fetch_all(roles=roles, locations=locations)

    if limit:
        jobs = jobs[:limit]

    return jobs
