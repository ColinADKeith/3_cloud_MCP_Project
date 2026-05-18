# 🤖 Weekly Autonomous Job Hunting Matrix

An enterprise-grade, cloud-orchestrated career intelligence pipeline that automates the end-to-end process of job discovery, semantic screening, and pipeline analytics. 

Every Sunday morning, this system autonomously spins up a cloud server, scrapes thousands of regional job listings, evaluates them mathematically against a professional resume profile using AI vector embeddings, updates a persistent data ledger, and compiles an executive Excel tracking dashboard.

---

## 🚀 Key Features

* **Autonomous Cloud Scheduling:** Fully orchestrated via GitHub Actions using a custom cron trigger—running completely serverless in the cloud every week without human intervention.
* **Targeted Deep Crawling:** Powered by Playwright (Headless Chromium) and BeautifulSoup4 to bypass dynamic client-side JavaScript layers and extract high-fidelity job listings and direct application URLs.
* **AI-Powered Semantic Screening:** Utilizes AWS Bedrock to generate multi-dimensional vector embeddings of job descriptions, executing low-latency cosine similarity matches against an Oracle 23ai Free Vector Database.
* **Persistent Deduplication Ledger:** Tracks unique fingerprint IDs mathematically generated from job metadata, ensuring old listings are automatically skipped to preserve API allocation limits and prevent noise.
* **Executive Excel Control Center:** Dynamically compiles qualified openings into an auto-formatted, conditional-formatted, production-ready Excel workbook (`.xlsx`) featuring an analytical KPI dashboard and automated data filtering.

---

## 🛠️ Architecture & Tech Stack

* **Runtime Environment:** Python 3.12, GitHub Actions Core (Ubuntu Runner)
* **Automation Framework:** Playwright, Beautiful Soup 4
* **AI Engine & Vector Embeddings:** AWS Bedrock (`amazon.titan-embed-text-v1`)
* **Database Infrastructure:** Oracle 23ai Free (Vector DB with True Cosine Distance Search)
* **Analytics Workbook Engine:** OpenPyXL
* **Version Control & Persistent State:** Git, Secure GitHub Repository Secrets

---

## 📁 Repository Structure

```text
3_cloud_MCP_Project/
├── .github/
│   └── workflows/
│       └── sunday_pipeline.yml     # GitHub Actions cloud cron configuration
├── data/
│   ├── processed_history.json      # Persistent master history log (deduplication)
│   ├── qualified_jobs.json        # Filtered JSON data payload of vector matches
│   └── Qualified_Job_Pipeline.xlsx # Main executive Excel dashboard sheet
├── network/
│   └── admin/                      # Secure Oracle DB Wallet Cloud credentials
└── src/
    ├── agents/
    │   └── Screener_agent.py       # Oracle 23ai Vector similarity screening engine
    ├── infrastructure/
    │   └── job_discovery.py        # Playwright web scraper for Job Bank Canada
    └── utils/
        ├── bedrock_guardrail.py    # AWS Bedrock vector generator link
        ├── export_excel.py         # OpenPyXL advanced spreadsheet compiler
        └── orchestrator.py         # Central pipeline master controller
