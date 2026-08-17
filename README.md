# Composio 100-App Buildability Research & Agent Pipeline

A two-pass AI research agent and human-in-the-loop verification pipeline for evaluating 100 software applications across 10 categories for **AI agent toolkit buildability** (auth method, access tier, API surface, existing MCPs, and buildability verdict).

- **Live Case Study:** [https://creative-madeleine-0a702d.netlify.app](https://creative-madeleine-0a702d.netlify.app)
- **GitHub Repository:** [https://github.com/TechySan031/composio-100](https://github.com/TechySan031/composio-100)

---

## 📊 Summary of Key Findings (across 100 apps)

- **Buildability Verdicts:** **64% Ready-Today**, **26% Buildable with Friction**, **10% Blocked**.
- **Auth Distribution:** OAuth2 dominates (**60%**), followed by API Keys (**50%**) and Bearer Tokens (**32%**). 42% support multiple auth methods.
- **Access Tiers:** **72% Self-Serve** (60% free tier/plan, 12% free trial), 16% paid plan gated, 5% partner gated, 4% approval gated.
- **Top Categories for Easy Wins:** Developer/Infra (100% self-serve) and Productivity/PM (100% self-serve).
- **Hardest Categories:** AI/Research (40% self-serve) and Finance/Fintech (50% self-serve).
- **Existing Ecosystem:** **20 of 100 apps** already have existing Model Context Protocol (MCP) servers (GitHub, Slack, Shopify, Notion, Stripe, Cloudflare, Supabase, etc.).

---

## 🏗️ Architecture & Pipeline Flow

```
+------------------+     +------------------------+     +----------------------+     +-----------------------+
|  apps_seed.py    | --> |       Pass 1           | --> |       Pass 2         | --> |   Human Verification  |
|  (100 Source     |     | Search Snippets        |     | Independent Docs     |     |   (20-App Sample      |
|   Apps)          |     | Extraction (Claude 4)  |     | Fetch & Self-Critique|     |    50% -> 100% Acc.)  |
+------------------+     +------------------------+     +----------------------+     +-----------------------+
                                                                                                 |
                                                                                                 v
                                                                                     +-----------------------+
                                                                                     |   site/index.html     |
                                                                                     |   (Standalone HTML    |
                                                                                     |    Case Study)        |
                                                                                     +-----------------------+
```

### Key Technical Improvements Implemented:
1. **Schema Validation (`schema.py`):** Pydantic `@model_validator` functions enforce cross-field constraints (`blocker` required when `buildability != 'ready-today'`, `has_existing_mcp` requires `mcp_evidence_url`).
2. **Confirmation Bias Mitigation (`agent.py`):** Pass 2 performs an independent search for primary developer documentation rather than relying solely on Pass 1 snippet URLs.
3. **SPA Docs Rendering (`tools.py`):** Leverages Tavily `client.extract()` for JS-rendered documentation sites (Mintlify, ReadMe, Docusaurus) with HTTP fallback and HTML entity cleaning.

---

## 🚀 Quickstart / How to Run

### 1. Prerequisites & Setup
```bash
git clone https://github.com/TechySan031/composio-100.git
cd composio-100

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` or set in your environment:
```ini
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...
TAVILY_API_KEY=tvly-...
```

### 3. Run Research Agent Pipeline
```bash
python agent.py
```
- Performs Pass 1 (snippets) & Pass 2 (docs fetch & verification) across all 100 apps.
- Output checkpointed to `data/pass1.json` and `data/pass2.json`.

### 4. Run Verification & Scoring
```bash
# Hand-verify sample:
python verify.py sample

# Score verification results:
python verify.py score
```
Outputs scored accuracy metrics to `data/verification_report.json`.

### 5. Run Pattern Analysis
```bash
python pattern_analysis.py
```
Outputs aggregated metrics to `data/patterns.json`.

### 6. Build Case Study HTML Page
```bash
python build_html.py
```
Generates the self-contained HTML case study at `site/index.html`.

---

## 📂 Repository Structure

```
.
├── README.md                 # Project documentation & runbook
├── schema.py                 # Pydantic data contract & cross-field validators
├── apps_seed.py              # 100 research target apps list
├── agent.py                  # Two-pass research pipeline
├── tools.py                  # Tavily search & JS-rendered page fetcher
├── verify.py                 # Human verification sampling & field accuracy scoring
├── pattern_analysis.py       # Aggregate metric analysis script
├── research_data.py          # Baseline research dataset generator
├── build_html.py             # HTML case study page generator
├── data/
│   ├── pass1.json            # First-pass agent research output
│   ├── pass2.json            # Second-pass verified agent research output
│   ├── human_checks.json     # 20-app hand-verification logs
│   ├── verification_report.json # Accuracy improvement report
│   ├── patterns.json         # Aggregated cross-app metrics
│   └── opus_qa_report.md     # Independent Senior QA Audit Report
└── site/
    └── index.html            # Standalone HTML case study (Deployed)
```

---

## 📜 License & Acknowledgments
Built for the Composio Senior AI Engineer Take-Home Assignment using Claude Sonnet 4, Tavily Search, Pydantic v2, and Vanilla CSS.
