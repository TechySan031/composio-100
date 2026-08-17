"""
The research agent. Two-pass design, this is the heart of the "verification
loop" story the assignment wants:

  PASS 1 (fast/cheap): one search, extract structured record from snippets only.
  PASS 2 (verify): does its OWN independent search for docs, fetches the actual
                    page text, re-extracts with real docs in context, and
                    self-critiques against pass 1. Any field it changes goes
                    into corrected_fields. This is what produces the
                    "accuracy went from X% to Y%" number.

Run this file directly to process all 100 apps and write data/pass1.json
and data/pass2.json. Designed to be resumable - re-running skips apps
already present in the output file.
"""
import os
import json
import time
from anthropic import Anthropic
from schema import AppRecord
from apps_seed import APPS
from tools import search, fetch_page_text

# Load .env file if present
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip().strip('"').strip("'")

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

EXTRACTION_TOOL = {
    "name": "record_app",
    "description": "Record structured research findings for one app.",
    "input_schema": AppRecord.model_json_schema(),
}


def _call_extractor(system: str, user: str) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=system,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "record_app"},
        messages=[{"role": "user", "content": user}],
    )
    for block in resp.content:
        if block.type == "tool_use":
            return block.input
    raise RuntimeError("Model did not return a tool_use block")


PASS1_SYSTEM = """You are a research analyst figuring out, for a given software \
app, how it could be turned into an AI-agent-callable toolkit. You are given \
web search snippets (not full docs). Extract what you can, and be honest: if \
snippets don't clearly show something, mark access_tier/buildability as \
'unknown'/'blocked' rather than guessing confidently. Every claim needs the \
evidence_url field set to the single most relevant snippet URL. Set \
confidence='agent-pass1' and agent_pass=1.

IMPORTANT rules:
- auth_methods: list ALL auth methods the app supports (e.g. both OAuth2 AND API Key if both exist)
- access_tier: be precise. 'self-serve-free' means a dev can get creds for free right now. \
  If it needs a paid plan, use 'paid-plan-gated'. If it needs sales contact, use 'partner-gated'.
- buildability: 'ready-today' ONLY if there are clear public docs AND self-serve auth. \
  If docs exist but access is gated, use 'buildable-with-friction'. If no API at all, use 'blocked'.
- For CLI-only tools with no web API, set api_type='None/Undocumented' and buildability='blocked' \
  (an agent toolkit needs a callable API, not just a CLI binary).
- blocker: MUST be set if buildability != 'ready-today'. Explain what blocks or adds friction."""

PASS2_SYSTEM = """You are verifying a first-pass research record against REAL \
fetched docs page text. You have TWO sources of information:
1. The pass-1 record (from search snippets only)
2. The ACTUAL fetched page text from the app's developer docs

Your job is to INDEPENDENTLY assess the app using the fetched docs, then compare \
with pass-1. For each field:
- If the docs CONFIRM pass-1's value, keep it.
- If the docs CONTRADICT or CLARIFY, CHANGE the field AND add its name to corrected_fields.
- If the docs are inaccessible ([FETCH_FAILED]), keep pass-1 values but do NOT raise confidence.

Set confidence='agent-pass2-verified' if you had usable page text, agent_pass=2.

IMPORTANT: Be skeptical of pass-1. It was built from search snippets which can be \
misleading. The fetched docs are the primary source of truth."""


def research_pass1(app: str, category: str, hint: str) -> dict:
    # Search without biasing toward any specific auth method
    results = search(f"{app} API developer docs authentication {hint}", max_results=5)
    snippets = "\n\n".join(
        f"URL: {r['url']}\nTITLE: {r['title']}\n{r['content'][:800]}"
        for r in results
    )
    user = f"App: {app}\nCategory: {category}\nHint: {hint}\n\nSearch snippets:\n{snippets}"
    record = _call_extractor(PASS1_SYSTEM, user)
    record["app"], record["category"] = app, category
    return record


def research_pass2(pass1_record: dict) -> dict:
    app = pass1_record["app"]
    hint = pass1_record.get("evidence_url", "")

    # Do an INDEPENDENT search for the app's docs (not just trusting pass1's URL)
    results = search(f"{app} API documentation authentication reference", max_results=3)
    # Also fetch the pass1 evidence URL for comparison
    urls_to_fetch = []
    if hint:
        urls_to_fetch.append(hint)
    for r in results:
        if r["url"] not in urls_to_fetch:
            urls_to_fetch.append(r["url"])
    urls_to_fetch = urls_to_fetch[:3]  # cap at 3 fetches

    page_texts = []
    for url in urls_to_fetch:
        text = fetch_page_text(url)
        if not text.startswith("[FETCH_FAILED"):
            page_texts.append(f"--- Source: {url} ---\n{text}")

    combined = "\n\n".join(page_texts) if page_texts else "[ALL_FETCHES_FAILED]"

    user = (
        f"PASS 1 RECORD:\n{json.dumps(pass1_record, indent=2)}\n\n"
        f"FETCHED DOCS TEXT (from {len(page_texts)} sources):\n{combined}"
    )
    record = _call_extractor(PASS2_SYSTEM, user)
    record["app"], record["category"] = pass1_record["app"], pass1_record["category"]
    return record


def _save(data: dict, path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def run_all(out_dir: str = "data"):
    os.makedirs(out_dir, exist_ok=True)
    p1_path = os.path.join(out_dir, "pass1.json")
    p2_path = os.path.join(out_dir, "pass2.json")

    pass1 = json.load(open(p1_path)) if os.path.exists(p1_path) else {}
    pass2 = json.load(open(p2_path)) if os.path.exists(p2_path) else {}

    total = len(APPS)
    for i, (app, category, hint) in enumerate(APPS, 1):
        if app not in pass1:
            print(f"[pass1] ({i}/{total}) {app} ...")
            try:
                pass1[app] = research_pass1(app, category, hint)
            except Exception as e:
                print(f"  FAILED: {e}")
                continue
            _save(pass1, p1_path)
            time.sleep(0.5)  # be polite to search API rate limits

    done = len(pass1)
    for i, app in enumerate(pass1, 1):
        if app not in pass2:
            print(f"[pass2] ({i}/{done}) {app} ...")
            try:
                pass2[app] = research_pass2(pass1[app])
            except Exception as e:
                print(f"  FAILED: {e}")
                continue
            _save(pass2, p2_path)
            time.sleep(0.3)

    print(f"\nDone. {len(pass1)} pass1 records, {len(pass2)} pass2 records in {out_dir}/")


if __name__ == "__main__":
    run_all()
