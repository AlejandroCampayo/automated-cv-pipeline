# Setup Guide

## Required: API Credentials

### 1. Gmail SMTP (for sending daily emails)

**Simple approach using App Password (recommended):**

1. Enable 2-Step Verification on your Google account: [myaccount.google.com/security](https://myaccount.google.com/security)
2. Generate an App Password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or your device)
   - Google will generate a 16-character password
3. Add to `.env.local`:
   ```
   GMAIL_ADDRESS=you@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

Done! No need for OAuth setup.

### 2. Gemini API (for grading job offers)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Create an API key (free tier)
3. Add to `.env.local`:
   ```
   GEMINI_API_KEY=your_key
   GEMINI_PROJECT_ID=your_project_id
   ```

### 3. Job Search Sources (choose at least one)

#### Option A: LinkedIn (requires login)
- Account credentials in `.env.local`

#### Option B: Indeed Job Scraper
- Cookie-based scraping (no auth needed)

#### Option C: Job APIs
- [JSearch API](https://rapidapi.com/Luchixo/api/jsearch) (requires RapidAPI key)
- [Serpapi Jobs](https://serpapi.com/) (paid, ~$100/mo)

## Configuration

1. **Create `config/job_preferences.md`** — specify locations, roles, and grading criteria
2. **Schedule the daily agent** at 8 AM via `/schedule`
3. **Test locally first** with `python scripts/daily_job_pipeline.py --dry-run`

## Security Notes

- `.env.local` is git-ignored — **never commit API keys**
- Store sensitive credentials in environment variables
- Rotate credentials periodically
- Use app-specific passwords for Gmail (not your main password)
