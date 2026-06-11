# Agent Guide (Application Strategy & Outreach)

Goal: Produce a `how_to_apply.md` that recommends HOW to apply (portal vs. direct cold outreach), identifies the right people to contact, infers reachable email addresses, and supplies a tailored cold-email draft.

## Inputs
- The job offer file in `job_offers/`.
- The matching `grading.md` (callback probability drives the apply-vs-coldmail call).
- A VERIFIED CONTACTS block supplied by the pipeline (extracted from the posting + a contacts
  search). You have NO web access when writing this document — work only from this block.

## Output
- Write `how_to_apply.md` inside the same `outputs/job_offers/<folder>/` as the CV.

## Apply-vs-cold-email decision rule
- **High portal callback probability (>55%)** and a real ATS: apply normally first; outreach only as a follow-up nudge.
- **Medium (35-55%)**: apply via portal AND send one direct cold email to a recruiter/hiring manager to jump the queue.
- **Low (<35%) or aggregator/black-box channel (e.g. Jobgether-style matching)**: prioritize direct outreach; the portal alone is low-yield.
- Always note when the posting is via an intermediary/agency vs. the employer directly — outreach targets differ.

## Contacts (use ONLY what you are given)
- Use ONLY the people and emails in the VERIFIED CONTACTS block. Do NOT invent names, titles,
  or LinkedIn/profile URLs, and do NOT guess a specific person from prior knowledge.
- If named people are provided, keep their links exactly as given (no edited or fabricated
  handles) and rank them by how directly they touch this role.
- If the block says NONE FOUND, name no one — advise searching LinkedIn for the company's
  recruiter or the hiring manager for this role, and applying via the portal.

## Email inference (be honest about confidence)
- Derive likely addresses only from a company's standard pattern, e.g. `first.last@company.com`.
- NEVER assert a private personal email as confirmed. Label every inferred address **(inferred, unverified)** and give the pattern it came from.
- Prefer verifiable role inboxes (careers@, jobs@, talent@, recruitment@) when the personal pattern is uncertain.
- Suggest a verification step (e.g. email-permutation + verifier tools, LinkedIn message as fallback).

## Formatting
- Output ONLY the finished `how_to_apply.md` in GitHub-flavoured Markdown. Do not restate
  these instructions or wrap the whole document in a code fence.
- Start with a single H1 title: `# How to Apply — <Company>: <Role>`, then a short bullet
  block: `- Date: <YYYY-MM-DD>` and `- Based on callback probability: **<band>** (see
  [grading.md](grading.md))`.

## Required sections in how_to_apply.md
1. **Header** — the title + bullet block described under Formatting.
2. **Recommendation** — one-line verdict (portal / portal+coldmail / coldmail-first) with the callback probability it is based on.
3. **Channel notes** — direct employer vs. agency/aggregator; where the real decision happens.
4. **Who to contact** — ONLY the people from the VERIFIED CONTACTS block (role, why them, the link as given), ranked. If none were provided, say so and advise searching LinkedIn — name no one.
5. **Reachable addresses** — verified role inboxes + inferred personal addresses (pattern + confidence + "(inferred, unverified)").
6. **Cold email draft** — subject + 120-160 word body tailored to the role, referencing 2-3 of the candidate's strongest matches from `grading.md`. Include a PDF-attached note.
7. **LinkedIn fallback** — short connection-request note (<300 chars).
8. **Timing & follow-up** — when to send, when to follow up once.

## Constraints
- Only use publicly available information; do not fabricate names or assert unverified emails as fact.
- Keep outreach honest — no fake mutual connections or invented referrals.
- Cold-email claims must match what the CV and `data/` actually support.
