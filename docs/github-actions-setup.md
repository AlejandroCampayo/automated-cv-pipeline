# Daily job digest via GitHub Actions (free)

This runs [`scripts/daily_job_pipeline.py`](../scripts/daily_job_pipeline.py) every
morning on GitHub's servers: **search all sources → grade with Gemini → auto-build
tailored CVs for strong matches → email you the matches with the CVs attached**. No
always-on machine needed. The workflow is
[`.github/workflows/daily-jobs.yml`](../.github/workflows/daily-jobs.yml).

## Job sources (all free)

The pipeline aggregates and de-duplicates across every available source
([`src/sources/`](../src/sources/)):

| Source | Key needed? | Coverage |
|---|---|---|
| **Moovijob** | no | Luxembourg (scraped) |
| **Arbeitnow** | no | EU + remote (public API) |
| **Remotive** | no | Remote tech/data (public API) |
| **Google Jobs** | `SERPAPI_KEY` (free tier ~100/mo) | Broad, per role × location |

LinkedIn is intentionally excluded (see the note at the bottom). Adding another
source is one small file in `src/sources/` plus a line in its registry.

## Cost: free

- **Public repo:** GitHub Actions minutes are unlimited.
- **Private repo:** 2000 free minutes/month. A daily ~5-minute run is ~150 min/month.
- **Gemini:** Google AI Studio free tier — one batched grading call per day is well within limits.
- **Gmail:** free (App Password over SMTP).

## ⚠️ Use a PRIVATE repo for the real thing

The pipeline needs your `config/job_preferences.md` (your skills, salary floor, and
the email it sends to). Keep that in a **private** GitHub repo so your preferences
aren't public. Your secrets (API keys, Gmail password) are **never committed** — they
go in GitHub's encrypted Secrets store.

## One-time setup

1. **Create a private repo and push this project to it:**
   ```bash
   gh repo create my-job-bot --private --source=. --push
   ```
   (or create it on github.com and `git push`). Make sure `config/job_preferences.md`
   is committed — it's needed by the run.

2. **Add Secrets** — repo → *Settings → Secrets and variables → Actions → New repository secret*.
   Add each of these (values come from your `.env.local`):

   | Secret | Required | What it is |
   |---|---|---|
   | `GEMINI_API_KEY` | ✅ | Google AI Studio key (grading + CV generation) |
   | `GMAIL_ADDRESS` | ✅ | the Gmail you send from |
   | `GMAIL_APP_PASSWORD` | ✅ | 16-char Gmail App Password (not your login password) |
   | `SERPAPI_KEY` | optional | enables the Google Jobs source (free tier ~100/mo) |
   | `GEMINI_PROJECT_ID` | optional | only if your setup needs it |

3. **Confirm the schedule.** Default cron is `0 6 * * *` (UTC) ≈ **08:00 in Luxembourg**
   during summer (CEST). In winter that's 07:00 local — change to `0 7 * * *` in the
   workflow if you want 08:00 year-round.

4. **Test it now** without waiting for 8am: repo → *Actions → Daily job digest → Run workflow*.
   Check your inbox and the run logs. The manual trigger has an optional
   **`strong_threshold`** input: set it to e.g. `25` for a one-off run that promotes any
   match scoring ≥ 25 to "strong", so the full CV pipeline fires even on a quiet day.
   Leave it blank for normal scheduled behavior — it's a test knob, not a permanent setting.

## Good to know

- GitHub may delay scheduled runs by a few minutes (sometimes more) under load — it's
  best-effort, not a hard alarm clock.
- On a repo with **no commits for 60 days**, GitHub auto-disables scheduled workflows.
  A manual *Run workflow* (or any push) re-enables it.
- The grading results JSON is uploaded as a build **artifact** (14-day retention) for
  debugging, separate from the email.
- **LinkedIn is intentionally not wired in.** Cookie-based LinkedIn scraping from CI IPs
  gets blocked/challenged fast and violates their ToS — it would break silently. Moovijob
  is the reliable source. Add other sources in `src/` if you have a stable API.

## Full pipeline — auto-generated CVs for strong matches

The workflow runs with `--full-pipeline`, so for every **strong** match the pipeline:

1. **Generates a tailored `cv.tex`** — Gemini fills the chosen template using *only* facts
   from your `data/` ([`src/cv_generator.py`](../src/cv_generator.py)), then compiles it to
   PDF. If the LaTeX fails to compile, the compiler error is fed back to the model and it
   retries — so a one-off bad escape doesn't lose the CV.
2. **Writes `grading.md` and `how_to_apply.md`** — detailed scorecard + apply strategy and
   a cold-email draft ([`src/full_pipeline.py`](../src/full_pipeline.py)).
3. **Attaches the full deliverable set to your digest email** — for each strong match:
   `cv.pdf`, the editable `cv.tex`, `grading.md`, `how_to_apply.md`, and the cached
   `offer.md`. Everything is also saved under
   `outputs/job_offers/<date>_<company>_<role>/` and uploaded as the `job-search-output`
   build artifact (14-day retention) — handy if you ran without email or want the raw files.

This needs your real `data/` in the (private) repo — it already is. The whole step is
**best-effort**: if generation or compilation fails for an offer, the daily digest still
goes out, just without that attachment.

Notes:
- It requires the LaTeX install step (already in the workflow) — adds ~1–2 min per run.
- **Gemini free-tier quotas matter.** Each strong match costs ~3 calls (CV + grading +
  how-to-apply). The default model is **`gemini-2.5-flash-lite`** because it has a large
  free *daily* quota; `gemini-2.5-flash` is capped at only ~20 requests/**day** on the
  free tier and will run dry fast. The pipeline backs off on per-*minute* limits and
  fails fast (no pointless waiting) on per-*day* caps. Override with the `GEMINI_MODEL`
  env var / repo variable if your key has different quota.
- **Real recruiter contacts** in `how_to_apply.md` come from the posting text plus a
  SerpAPI LinkedIn search ([`src/contact_finder.py`](../src/contact_finder.py)) — never
  fabricated. The search runs once per strong match and shares the SerpAPI free quota
  (~100/mo); without `SERPAPI_KEY` it falls back to "search LinkedIn for the recruiter".
- To get the digest **without** auto-CVs, drop `--full-pipeline` from the workflow's run step.
