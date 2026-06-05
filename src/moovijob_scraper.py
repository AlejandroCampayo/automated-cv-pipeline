"""Moovijob job scraper using Playwright."""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time

# Map roles to Moovijob field URLs
FIELD_URLS = [
    "https://en.moovijob.com/job-offers/jobs-luxembourg/field-it-development",
]

# Keywords that must appear in title to be worth fetching description for
RELEVANT_TITLE_KEYWORDS = [
    "machine learning", "ml ", "ai ", "artificial intelligence",
    "data scientist", "data science", "deep learning", "computer vision",
    "nlp", "llm", "neural", "pytorch", "tensorflow",
    "data engineer", "data analyst", "perception", "algorithm",
    "research engineer", "vision", "autonomous",
]

BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


async def _fetch_page(browser, url, wait_ms=3000):
    """Fetch a page and return its HTML."""
    page = await browser.new_page(user_agent=BROWSER_UA)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(wait_ms)
        return await page.content()
    finally:
        await page.close()


def _parse_listing_page(html):
    """Parse job listing page and return list of job dicts (title, company, url, date)."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("li", class_="company-item")
    jobs = []
    for card in cards:
        title_elem = card.find(class_="card-job-offer-new-title")
        company_elem = card.find(class_="company-name")
        date_elem = card.find(class_="published_ago")
        link = card.find("a", href=True)

        title = title_elem.get_text(strip=True) if title_elem else ""
        company = company_elem.get_text(strip=True) if company_elem else ""
        date = date_elem.get_text(strip=True) if date_elem else ""
        url = link["href"] if link else ""

        if title and company and url:
            jobs.append({
                "title": title,
                "company": company,
                "location": "Luxembourg",
                "url": url if url.startswith("http") else f"https://en.moovijob.com{url}",
                "posted_date": date,
                "description": "",
                "salary": None,
                "source": "Moovijob",
            })
    return jobs


def _parse_job_description(html):
    """Extract description text from a job detail page."""
    soup = BeautifulSoup(html, "html.parser")

    # Job metadata (contract type, language, experience)
    meta_row = soup.find("div", class_="row")
    meta = meta_row.get_text(separator=" ", strip=True) if meta_row else ""

    # Description: plain <p> tags in the main content column
    # They appear before the sidebar and contain the actual job text
    sidebar = soup.find(class_="job-offer-sidebar")
    description_parts = []

    if sidebar:
        # Walk backwards from the sidebar to collect all <p> and <li> in the same section
        main_col = sidebar.find_previous_sibling()
        if main_col:
            for elem in main_col.find_all(["p", "li", "h2", "h3", "h4"]):
                text = elem.get_text(strip=True)
                if text and len(text) > 15:
                    description_parts.append(text)

    # Fallback: grab all bare <p> tags on the page with real content
    if not description_parts:
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 40:
                description_parts.append(text)

    description = "\n".join(description_parts[:20])  # Cap at 20 lines
    if meta:
        description = meta + "\n\n" + description
    return description[:2000]


async def scrape_moovijob(fetch_descriptions=True):
    """
    Scrape job listings from Moovijob Luxembourg.

    Args:
        fetch_descriptions: If True, visit each job page to get description

    Returns:
        List of job dicts
    """
    all_jobs = []
    seen_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            # 1. Scrape listing pages
            for field_url in FIELD_URLS:
                print(f"    Listing: {field_url.split('/')[-1]}")
                try:
                    html = await _fetch_page(browser, field_url)
                    jobs = _parse_listing_page(html)
                    for job in jobs:
                        if job["url"] not in seen_urls:
                            all_jobs.append(job)
                            seen_urls.add(job["url"])
                    print(f"    → {len(jobs)} jobs")
                except Exception as e:
                    print(f"    Listing error: {e}")

            # 2. Fetch descriptions only for title-relevant jobs
            if fetch_descriptions and all_jobs:
                relevant = [
                    j for j in all_jobs
                    if any(kw in j["title"].lower() for kw in RELEVANT_TITLE_KEYWORDS)
                ]
                print(f"\n    {len(relevant)}/{len(all_jobs)} jobs match keywords — fetching descriptions...")
                for i, job in enumerate(relevant):
                    try:
                        desc_html = await _fetch_page(browser, job["url"], wait_ms=3000)
                        job["description"] = _parse_job_description(desc_html)
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"    Description error for {job['title']}: {e}")

        finally:
            await browser.close()

    return all_jobs


def scrape_moovijob_sync(fetch_descriptions=True):
    """Synchronous wrapper."""
    try:
        return asyncio.run(scrape_moovijob(fetch_descriptions=fetch_descriptions))
    except Exception as e:
        print(f"Scraper error: {e}")
        return []
