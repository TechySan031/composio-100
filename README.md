# Composio 100-App Research Agent — Runbook

Everything below is the exact sequence to go from an empty repo to a
submitted, deployed case study. Follow in order.

## 0. Prerequisites (10 min)
```bash
cd composio-100
python -m venv venv && source venv/bin/activate   # or use conda
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-ant-..."
export TAVILY_API_KEY="tvly-..."
```
Get Tavily key free at tavily.com (no card needed). Anthropic key from
console.anthropic.com.

## 1. Sanity-check the schema and seed list (already done)
- `schema.py` — the record shape every app gets
- `apps_seed.py` — all 100 apps, category, hint URL. Asserted to be exactly 100.

## 2. Run Pass 1 across all 100 apps (~15-25 min, unattended)
```bash
python agent.py
```
This does BOTH passes in one run: pass 1 (search snippets → extract) then
pass 2 (fetch the evidence URL → re-extract → self-critique against pass 1).
It's resumable — if it dies partway (rate limit, network blip), just re-run;
it skips apps already in `data/pass1.json` / `data/pass2.json`.

Watch the terminal output. Note which apps fail fetch (`[FETCH_FAILED]`) —
these are honest data points for your page, not bugs to hide (some docs
sites block bots; that's a real finding about API accessibility too).

## 3. Hand-verify a sample (~45-60 min) — THIS IS THE PART THAT MATTERS MOST
```bash
python verify.py sample
```
This prints ~20 random apps with pass1 vs pass2 side by side and writes
`data/human_checks_TEMPLATE.json`. For each app:
1. Open the `evidence_url` yourself
2. Check: is the auth method right? Is access_tier right? Is buildability right?
3. Fill in `pass1_correct` / `pass2_correct` (true/false) and note which
   fields pass1 got wrong in `wrong_fields_pass1`
4. Save the file as `data/human_checks.json`

Then:
```bash
python verify.py score
```
This gives you the real number: **pass1 accuracy vs pass2 accuracy on your
sample** — e.g. "68% → 91%". This is the single most important stat on
your whole page. Don't skip apps that were wrong — those are the most
convincing part of the submission.

If pass2 accuracy is still weak on specific apps, manually correct those
records directly in `data/pass2.json`, set `"confidence": "human-corrected"`,
and list what you changed in `corrected_fields`. That's a legitimate third
tier and honest to show.

## 4. Run pattern analysis (2 min)
```bash
python pattern_analysis.py
```
Writes `data/patterns.json` — auth method distribution, access tier
distribution, self-serve % by category, top blockers, ready-today vs
blocked apps. Read the output. Pick your actual headline claims from
what's really there — don't force a narrative that isn't supported.

## 5. Build the HTML page
Come back to me here with `data/pass2.json`, `data/patterns.json`, and
`data/verification_report.json` and I'll build the single-page case study:
headline patterns → skimmable matrix → agent architecture diagram →
verification results (honest) → proof/demo. I need the real data in hand
to build this well rather than guessing at numbers.

## 6. Repo hygiene (10 min)
- Make sure `.env` / API keys are NOT committed (add `.gitignore`)
- This README is your submitted README — check it still reads clean
- Push to GitHub

## 7. Deploy (10 min)
Static single HTML file → drag-and-drop deploy:
- **Netlify**: app.netlify.com/drop → drag the `site/index.html` folder
- **Vercel**: `vercel --prod` in the site folder
- **GitHub Pages**: enable Pages on the repo, point at `/site`

## 8. Submit
- Live link to the deployed HTML page
- Link to the source repo (this one)

---

## Honesty notes for the write-up
- If Composio already has a toolkit/MCP for an app, say so — that's a
  valid "ready-today, and here's proof it's already been done" finding.
- If an app is genuinely undiscoverable via public docs (paywalled,
  contact-sales only), the correct output is "blocked — partner-gated,
  evidence: <sales page>", not a guess.
- Where the agent's pass1 was wrong and pass2 fixed it, or where a human
  had to fix it — show it. That's the whole point of the assignment.
