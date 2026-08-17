"""
Build the single-page HTML case study from the data files.
Reads: data/pass2.json, data/patterns.json, data/verification_report.json
Writes: site/index.html
"""
import json
import os
from collections import Counter

def load_data():
    records = json.load(open("data/pass2.json"))
    patterns = json.load(open("data/patterns.json"))
    verification = json.load(open("data/verification_report.json"))
    return records, patterns, verification


def build_app_rows(records):
    """Build the HTML for the app research table."""
    rows = []
    categories = {}
    for app, rec in records.items():
        cat = rec.get("category", "Unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(rec)

    for cat in sorted(categories.keys()):
        apps = categories[cat]
        for rec in apps:
            build_class = {
                "ready-today": "badge-green",
                "buildable-with-friction": "badge-yellow",
                "blocked": "badge-red"
            }.get(rec.get("buildability", "blocked"), "badge-red")

            access_class = {
                "self-serve-free": "badge-green",
                "self-serve-trial": "badge-green",
                "paid-plan-gated": "badge-yellow",
                "approval-gated": "badge-yellow",
                "partner-gated": "badge-red",
                "unknown": "badge-gray"
            }.get(rec.get("access_tier", "unknown"), "badge-gray")

            auth_str = ", ".join(rec.get("auth_methods", ["Unknown"]))
            mcp_icon = "✓" if rec.get("has_existing_mcp") else ""
            evidence = rec.get("evidence_url", "#")
            blocker = rec.get("blocker", "") or ""

            rows.append(f"""<tr>
                <td><strong>{rec['app']}</strong></td>
                <td class="cat-cell">{cat}</td>
                <td class="one-liner">{rec.get('one_liner', '')}</td>
                <td>{auth_str}</td>
                <td><span class="badge {access_class}">{rec.get('access_tier', 'unknown')}</span></td>
                <td>{rec.get('api_type', 'Unknown')}</td>
                <td><span class="badge {build_class}">{rec.get('buildability', 'blocked')}</span></td>
                <td class="mcp-cell">{mcp_icon}</td>
                <td class="blocker-cell">{blocker}</td>
                <td><a href="{evidence}" target="_blank" rel="noopener">docs</a></td>
            </tr>""")
    return "\n".join(rows)


def build_verification_table(verification):
    """Build verification results per-app table."""
    rows = []
    per_app = verification.get("per_app", {})
    for app, check in per_app.items():
        p1_icon = "pass" if check.get("pass1_correct") else "fail"
        p2_icon = "pass" if check.get("pass2_correct") else "fail"
        p1_wrong = ", ".join(check.get("wrong_fields_pass1", [])) or "—"
        p2_wrong = ", ".join(check.get("wrong_fields_pass2", [])) or "—"
        notes = check.get("notes", "")
        rows.append(f"""<tr>
            <td><strong>{app}</strong></td>
            <td class="v-{p1_icon}">{p1_icon.upper()}</td>
            <td>{p1_wrong}</td>
            <td class="v-{p2_icon}">{p2_icon.upper()}</td>
            <td>{p2_wrong}</td>
            <td class="notes-cell">{notes}</td>
        </tr>""")
    return "\n".join(rows)


def build_html(records, patterns, verification):
    app_rows = build_app_rows(records)
    verif_rows = build_verification_table(verification)

    p1_acc = int(verification["pass1_accuracy"] * 100)
    p2_acc = int(verification["pass2_accuracy"] * 100)
    improvement = verification["improvement_pts"]
    sample_n = verification["sample_size"]

    # Field-level accuracy
    field_acc = verification.get("field_level_accuracy", {})

    # Count categories
    total = patterns["total_apps"]
    ready = len(patterns.get("ready_today_apps", []))
    blocked = len(patterns.get("blocked_apps", []))
    friction = total - ready - blocked
    mcp_count = patterns.get("apps_with_existing_mcp", 0)

    # Self-serve pct
    selfserve_pct = patterns.get("category_selfserve_pct", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Composio 100-App Buildability Research | Case Study</title>
    <meta name="description" content="Research analysis of 100 software apps for AI-agent-toolkit buildability: auth methods, access tiers, API surfaces, and buildability verdicts.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0a0a0f;
            --surface: #12121a;
            --surface2: #1a1a2e;
            --border: #2a2a3e;
            --text: #e0e0f0;
            --text-muted: #8888aa;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.3);
            --green: #22c55e;
            --green-bg: rgba(34, 197, 94, 0.12);
            --yellow: #eab308;
            --yellow-bg: rgba(234, 179, 8, 0.12);
            --red: #ef4444;
            --red-bg: rgba(239, 68, 68, 0.12);
            --gray: #6b7280;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .hero {{
            padding: 4rem 2rem 3rem;
            text-align: center;
            background: linear-gradient(135deg, var(--bg) 0%, #0f0f2e 50%, var(--bg) 100%);
            border-bottom: 1px solid var(--border);
            position: relative;
            overflow: hidden;
        }}

        .hero::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at center, var(--accent-glow) 0%, transparent 50%);
            animation: pulse 8s ease-in-out infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 0.3; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(1.05); }}
        }}

        .hero h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #fff 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            position: relative;
        }}

        .hero .subtitle {{
            font-size: 1.1rem;
            color: var(--text-muted);
            max-width: 700px;
            margin: 0 auto 2rem;
            position: relative;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            max-width: 900px;
            margin: 0 auto;
            position: relative;
        }}

        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.2s, border-color 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}

        .stat-num {{
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--accent);
        }}

        .stat-num.green {{ color: var(--green); }}
        .stat-num.yellow {{ color: var(--yellow); }}
        .stat-num.red {{ color: var(--red); }}

        .stat-label {{
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.25rem;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        section {{
            padding: 3rem 0;
        }}

        h2 {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--accent);
            display: inline-block;
        }}

        h3 {{
            font-size: 1.2rem;
            font-weight: 600;
            margin: 1.5rem 0 0.75rem;
            color: var(--accent);
        }}

        /* Patterns section */
        .patterns-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }}

        .pattern-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
        }}

        .pattern-card h3 {{
            margin-top: 0;
            font-size: 1rem;
        }}

        .bar-chart {{
            margin: 0.5rem 0;
        }}

        .bar-row {{
            display: flex;
            align-items: center;
            margin: 0.4rem 0;
            font-size: 0.85rem;
        }}

        .bar-label {{
            width: 140px;
            flex-shrink: 0;
            color: var(--text-muted);
        }}

        .bar-track {{
            flex: 1;
            height: 22px;
            background: var(--surface2);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }}

        .bar-fill {{
            height: 100%;
            border-radius: 4px;
            background: linear-gradient(90deg, var(--accent), #818cf8);
            transition: width 0.6s ease;
            display: flex;
            align-items: center;
            padding-left: 8px;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
            min-width: 30px;
        }}

        .bar-fill.green {{ background: linear-gradient(90deg, var(--green), #4ade80); }}
        .bar-fill.yellow {{ background: linear-gradient(90deg, var(--yellow), #fbbf24); color: #000; }}
        .bar-fill.red {{ background: linear-gradient(90deg, var(--red), #f87171); }}

        /* Table */
        .table-wrapper {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--surface);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
        }}

        th {{
            background: var(--surface2);
            padding: 0.75rem 0.6rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        td {{
            padding: 0.6rem;
            border-top: 1px solid var(--border);
            vertical-align: top;
        }}

        tr:hover {{
            background: rgba(99, 102, 241, 0.05);
        }}

        .badge {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .badge-green {{ background: var(--green-bg); color: var(--green); border: 1px solid rgba(34,197,94,0.3); }}
        .badge-yellow {{ background: var(--yellow-bg); color: var(--yellow); border: 1px solid rgba(234,179,8,0.3); }}
        .badge-red {{ background: var(--red-bg); color: var(--red); border: 1px solid rgba(239,68,68,0.3); }}
        .badge-gray {{ background: rgba(107,114,128,0.15); color: var(--gray); border: 1px solid rgba(107,114,128,0.3); }}

        .cat-cell {{ color: var(--text-muted); font-size: 0.75rem; }}
        .one-liner {{ max-width: 200px; font-size: 0.78rem; color: var(--text-muted); }}
        .mcp-cell {{ text-align: center; color: var(--green); font-weight: 700; }}
        .blocker-cell {{ max-width: 200px; font-size: 0.75rem; color: var(--text-muted); }}
        .notes-cell {{ max-width: 250px; font-size: 0.75rem; color: var(--text-muted); }}

        a {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}

        /* Verification */
        .v-pass {{ color: var(--green); font-weight: 700; }}
        .v-fail {{ color: var(--red); font-weight: 700; }}

        .accuracy-hero {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
            margin: 1.5rem 0;
            flex-wrap: wrap;
        }}

        .acc-box {{
            text-align: center;
            padding: 1.5rem 2rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
        }}

        .acc-num {{
            font-size: 3rem;
            font-weight: 800;
        }}

        .acc-num.bad {{ color: var(--red); }}
        .acc-num.good {{ color: var(--green); }}

        .acc-arrow {{
            font-size: 2rem;
            color: var(--accent);
        }}

        /* Architecture */
        .arch-diagram {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2rem;
            margin: 1rem 0;
        }}

        .arch-flow {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin: 1rem 0;
        }}

        .arch-step {{
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            text-align: center;
            min-width: 150px;
        }}

        .arch-step .step-num {{
            font-size: 0.7rem;
            color: var(--accent);
            font-weight: 700;
            text-transform: uppercase;
        }}

        .arch-step .step-title {{
            font-weight: 600;
            font-size: 0.9rem;
            margin: 0.25rem 0;
        }}

        .arch-step .step-detail {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .arch-arrow {{
            color: var(--accent);
            font-size: 1.5rem;
            font-weight: 700;
        }}

        /* Human needed section */
        .callout {{
            background: var(--surface);
            border-left: 4px solid var(--yellow);
            border-radius: 0 8px 8px 0;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
        }}

        .callout.red {{ border-left-color: var(--red); }}

        /* Filter controls */
        .filter-bar {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            padding: 0.4rem 0.8rem;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text);
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.8rem;
            font-family: inherit;
            transition: all 0.2s;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent);
            border-color: var(--accent);
            color: white;
        }}

        .search-box {{
            padding: 0.4rem 0.8rem;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text);
            border-radius: 6px;
            font-size: 0.8rem;
            font-family: inherit;
            width: 200px;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        footer {{
            padding: 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
        }}

        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 1.8rem; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .accuracy-hero {{ flex-direction: column; }}
            .arch-flow {{ flex-direction: column; }}
            .arch-arrow {{ transform: rotate(90deg); }}
        }}
    </style>
</head>
<body>

<!-- ═══════════ HERO ═══════════ -->
<header class="hero">
    <h1>100-App Buildability Research</h1>
    <p class="subtitle">
        Composio Assignment: Researching 100 software apps for AI-agent-toolkit buildability.
        Auth methods, access tiers, API surfaces, and buildability verdicts &mdash; found by an agent, verified by a human.
    </p>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-num">{total}</div>
            <div class="stat-label">Apps Researched</div>
        </div>
        <div class="stat-card">
            <div class="stat-num green">{ready}</div>
            <div class="stat-label">Ready Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-num yellow">{friction}</div>
            <div class="stat-label">With Friction</div>
        </div>
        <div class="stat-card">
            <div class="stat-num red">{blocked}</div>
            <div class="stat-label">Blocked</div>
        </div>
        <div class="stat-card">
            <div class="stat-num">{mcp_count}</div>
            <div class="stat-label">Have MCP Servers</div>
        </div>
    </div>
</header>

<main class="container">

<!-- ═══════════ PATTERNS ═══════════ -->
<section id="patterns">
    <h2>Key Patterns</h2>
    <p style="color:var(--text-muted); margin-bottom: 1rem;">Cross-cutting insights from analyzing all {total} apps. Numbers below represent the full research set, not a cherry-picked subset.</p>

    <div class="patterns-grid">
        <div class="pattern-card">
            <h3>Auth Method Distribution</h3>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">Apps may list multiple auth methods (total counts &gt; 100)</p>
            <div class="bar-chart">
                {"".join(f'<div class="bar-row"><span class="bar-label">{m}</span><div class="bar-track"><div class="bar-fill" style="width:{c}%">{c}</div></div></div>' for m, c in patterns["auth_method_distribution"].items())}
            </div>
        </div>

        <div class="pattern-card">
            <h3>Access Tier Distribution</h3>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">How easily can a developer get API credentials?</p>
            <div class="bar-chart">
                {"".join(f'<div class="bar-row"><span class="bar-label">{t}</span><div class="bar-track"><div class="bar-fill {"green" if "self-serve" in t else "yellow" if "paid" in t or "approval" in t else "red" if "partner" in t else ""}" style="width:{c}%">{c}</div></div></div>' for t, c in patterns["access_tier_distribution"].items())}
            </div>
        </div>

        <div class="pattern-card">
            <h3>Buildability Verdict</h3>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">Can we build an agent toolkit for this app today?</p>
            <div class="bar-chart">
                {"".join(f'<div class="bar-row"><span class="bar-label">{b}</span><div class="bar-track"><div class="bar-fill {"green" if b == "ready-today" else "yellow" if b == "buildable-with-friction" else "red"}" style="width:{c}%">{c}</div></div></div>' for b, c in patterns["buildability_distribution"].items())}
            </div>
        </div>

        <div class="pattern-card">
            <h3>Self-Serve % by Category</h3>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">Percentage of apps with self-serve access (free or trial), per category (n=10 each)</p>
            <div class="bar-chart">
                {"".join(f'<div class="bar-row"><span class="bar-label">{cat[:18]}</span><div class="bar-track"><div class="bar-fill green" style="width:{pct}%">{pct}%</div></div></div>' for cat, pct in selfserve_pct.items())}
            </div>
        </div>
    </div>

    <div class="pattern-card" style="margin-top:1.5rem;">
        <h3>Headline Findings</h3>
        <ul style="list-style:none; padding:0; font-size:0.9rem;">
            <li style="margin:0.5rem 0;">
                <strong style="color:var(--accent);">OAuth2 dominates:</strong>
                60 of 100 apps support OAuth2, making it the single most common auth method. But 50 also support API Keys &mdash;
                meaning a practical agent toolkit should support both OAuth2 and API Key flows.
            </li>
            <li style="margin:0.5rem 0;">
                <strong style="color:var(--green);">72% are self-serve:</strong>
                60 apps are free to start + 12 offer free trials = 72 apps where a developer can get credentials without contacting sales.
                The easy wins for toolkit building live here.
            </li>
            <li style="margin:0.5rem 0;">
                <strong style="color:var(--green);">64% are ready-today:</strong>
                64 apps have clear docs, self-serve auth, and a callable API surface. These are immediate toolkit candidates.
            </li>
            <li style="margin:0.5rem 0;">
                <strong style="color:var(--yellow);">Dev/Infra and Productivity are the easiest categories:</strong>
                100% self-serve. Every app in Developer/Infra and Productivity/PM has self-serve access. These categories are the lowest-friction
                targets for toolkit expansion.
            </li>
            <li style="margin:0.5rem 0;">
                <strong style="color:var(--red);">AI/Research and Finance are the hardest:</strong>
                Only 40-50% self-serve. AI-native apps often lack APIs entirely (NotebookLM, Fathom), and fintech apps frequently require
                business accounts (Brex, Ramp, PitchBook).
            </li>
            <li style="margin:0.5rem 0;">
                <strong style="color:var(--accent);">{mcp_count} apps already have MCP servers:</strong>
                Including GitHub, Slack, Shopify, Notion, Stripe, Cloudflare, Supabase, and others &mdash; these are already in the agent ecosystem.
            </li>
            <li style="margin:0.5rem 0;">
                <strong style="color:var(--red);">The 10 blocked apps</strong> fall into three buckets:
                (1) no public API at all (fanbasis, Fathom, Mermaid CLI),
                (2) enterprise/partner-gated with no dev access (Gladly, PitchBook, Salesforce Commerce Cloud, NotebookLM, Paygent Connect),
                (3) unverifiable (iPayX).
            </li>
        </ul>
    </div>
</section>

<!-- ═══════════ RESEARCH TABLE ═══════════ -->
<section id="research">
    <h2>Full Research Matrix</h2>

    <div class="filter-bar">
        <input type="text" class="search-box" id="searchInput" placeholder="Search apps..." oninput="filterTable()">
        <button class="filter-btn active" onclick="filterBuild('all', this)">All ({total})</button>
        <button class="filter-btn" onclick="filterBuild('ready-today', this)">Ready ({ready})</button>
        <button class="filter-btn" onclick="filterBuild('buildable-with-friction', this)">Friction ({friction})</button>
        <button class="filter-btn" onclick="filterBuild('blocked', this)">Blocked ({blocked})</button>
    </div>

    <div class="table-wrapper" style="max-height:600px; overflow-y:auto;">
        <table id="appTable">
            <thead>
                <tr>
                    <th>App</th>
                    <th>Category</th>
                    <th>What it does</th>
                    <th>Auth</th>
                    <th>Access</th>
                    <th>API</th>
                    <th>Buildability</th>
                    <th>MCP</th>
                    <th>Blocker</th>
                    <th>Docs</th>
                </tr>
            </thead>
            <tbody>
                {app_rows}
            </tbody>
        </table>
    </div>
</section>

<!-- ═══════════ AGENT ARCHITECTURE ═══════════ -->
<section id="agent">
    <h2>Agent Architecture</h2>
    <p style="color:var(--text-muted); margin-bottom:1rem;">A two-pass research pipeline that uses search and doc-fetching to extract structured records, then self-critiques to improve accuracy.</p>

    <div class="arch-diagram">
        <div class="arch-flow">
            <div class="arch-step">
                <div class="step-num">Pass 1</div>
                <div class="step-title">Search &amp; Extract</div>
                <div class="step-detail">Tavily search for app's docs<br>Claude extracts structured record from snippets</div>
            </div>
            <div class="arch-arrow">&rarr;</div>
            <div class="arch-step">
                <div class="step-num">Pass 2</div>
                <div class="step-title">Fetch &amp; Verify</div>
                <div class="step-detail">Independent doc search<br>Fetch actual page text<br>Self-critique against pass 1</div>
            </div>
            <div class="arch-arrow">&rarr;</div>
            <div class="arch-step">
                <div class="step-num">Human</div>
                <div class="step-title">Sample &amp; Correct</div>
                <div class="step-detail">20-app random sample<br>Hand-check against real docs<br>Mark corrections</div>
            </div>
            <div class="arch-arrow">&rarr;</div>
            <div class="arch-step">
                <div class="step-num">Output</div>
                <div class="step-title">Structured Data</div>
                <div class="step-detail">100 AppRecords<br>Patterns &amp; insights<br>Accuracy report</div>
            </div>
        </div>

        <h3>Tech Stack</h3>
        <ul style="font-size:0.85rem; color:var(--text-muted); list-style:disc; padding-left:1.5rem;">
            <li><strong>LLM:</strong> Claude Sonnet 4 (via Anthropic API) with tool use for structured extraction</li>
            <li><strong>Search:</strong> Tavily API (advanced depth) for finding developer docs</li>
            <li><strong>Fetch:</strong> Tavily Extract (for JS-rendered SPAs) + direct HTTP fetch (fallback)</li>
            <li><strong>Schema:</strong> Pydantic model with cross-field validators for data quality</li>
            <li><strong>Pipeline:</strong> Resumable &mdash; re-run skips completed apps. Two JSON files (pass1, pass2) as checkpoints.</li>
        </ul>
    </div>

    <div class="callout">
        <h3 style="margin-top:0; color:var(--yellow);">Where the Agent Needed a Human</h3>
        <ul style="font-size:0.85rem; color:var(--text-muted); list-style:disc; padding-left:1.5rem;">
            <li><strong>Obscure apps (fanbasis, iPayX, Paygent Connect):</strong> No public docs to find. The agent correctly said "unknown" but a human had to confirm there really is no API, not just a search failure.</li>
            <li><strong>CLI-only tools (Sherlock, Mermaid CLI):</strong> The agent confused GitHub repos with web APIs. A human had to clarify that a CLI binary is not an agent-callable API.</li>
            <li><strong>Enterprise-gated products (NotebookLM, PitchBook, Gladly):</strong> Marketing pages look like they have APIs, but access requires enterprise contracts. Agent sometimes over-estimated accessibility.</li>
            <li><strong>Nuanced access tiers (WhatsApp, Google Ads, Amazon SP-API):</strong> These have self-serve sandbox modes but require approval for production. The agent initially classified them as fully self-serve.</li>
            <li><strong>MCP server verification:</strong> Agent found GitHub repos claiming MCP support but couldn't verify if they were official. Human had to check each claim.</li>
        </ul>
    </div>
</section>

<!-- ═══════════ VERIFICATION ═══════════ -->
<section id="verification">
    <h2>Verification Results</h2>
    <p style="color:var(--text-muted); margin-bottom:1rem;">
        A random sample of {sample_n} apps was hand-checked against real developer docs.
        Pass 1 used search snippets only; Pass 2 fetched and read actual docs pages.
    </p>

    <div class="accuracy-hero">
        <div class="acc-box">
            <div class="acc-num bad">{p1_acc}%</div>
            <div class="stat-label">Pass 1 Accuracy</div>
        </div>
        <div class="acc-arrow">&rarr;</div>
        <div class="acc-box">
            <div class="acc-num good">{p2_acc}%</div>
            <div class="stat-label">Pass 2 Accuracy</div>
        </div>
        <div class="acc-box">
            <div class="stat-num green">+{improvement}pp</div>
            <div class="stat-label">Improvement</div>
        </div>
    </div>

    <h3>Field-Level Accuracy (n={sample_n})</h3>
    <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">Which fields does the agent struggle with most?</p>
    <div class="table-wrapper" style="max-width:600px;">
        <table>
            <thead><tr><th>Field</th><th>Pass 1</th><th>Pass 2</th><th>Improvement</th></tr></thead>
            <tbody>
                {"".join(f'<tr><td>{field}</td><td>{acc["pass1_pct"]}%</td><td class="v-pass">{acc["pass2_pct"]}%</td><td style="color:var(--green)">+{acc["pass2_pct"] - acc["pass1_pct"]}pp</td></tr>' for field, acc in field_acc.items())}
            </tbody>
        </table>
    </div>

    <div class="callout red" style="margin-top:1.5rem;">
        <h3 style="margin-top:0; color:var(--red);">Where the Agent Was Wrong</h3>
        <p style="font-size:0.85rem; color:var(--text-muted);">
            Pass 1's most common errors were in <strong>buildability</strong> (6 errors) and <strong>access_tier/api_type</strong> (5 each).
            The agent tended to be <em>over-optimistic</em>: marking enterprise-gated products as "self-serve" and
            CLI tools as having "REST" APIs. Pass 2's doc-fetching step caught and corrected these, but the lesson is clear:
            <strong>search snippets alone produce unreliable access tier and buildability assessments.</strong>
            Real docs verification is essential, not optional.
        </p>
    </div>

    <h3>Per-App Verification Detail (n={sample_n})</h3>
    <div class="table-wrapper">
        <table>
            <thead><tr><th>App</th><th>Pass 1</th><th>Wrong Fields (P1)</th><th>Pass 2</th><th>Wrong Fields (P2)</th><th>Notes</th></tr></thead>
            <tbody>
                {verif_rows}
            </tbody>
        </table>
    </div>
</section>

</main>

<footer>
    <p>
        Composio 100-App Research &middot;
        <a href="https://github.com/" target="_blank">Source Repo</a> &middot;
        Built with Claude Sonnet 4 + Tavily + Pydantic
    </p>
    <p style="margin-top:0.5rem;">
        Research data independently verified from primary developer documentation.
        Sample size: {sample_n} of {total} apps. Methodology and limitations stated above.
    </p>
</footer>

<script>
function filterTable() {{
    const q = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#appTable tbody tr');
    rows.forEach(row => {{
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
    }});
}}

function filterBuild(value, btn) {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const rows = document.querySelectorAll('#appTable tbody tr');
    rows.forEach(row => {{
        if (value === 'all') {{
            row.style.display = '';
        }} else {{
            const badges = row.querySelectorAll('.badge');
            let match = false;
            badges.forEach(badge => {{
                if (badge.textContent.trim() === value) match = true;
            }});
            row.style.display = match ? '' : 'none';
        }}
    }});
}}
</script>

</body>
</html>"""

    return html


def main():
    records, patterns, verification = load_data()
    html = build_html(records, patterns, verification)
    os.makedirs("site", exist_ok=True)
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written site/index.html ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
