# 🛡️ ScopeGuard AI — Client Scope Creep & Change Order Engine
> **An AI SaaS application empowering digital agencies, software shops, and freelance consultants to protect profit margins from unbilled scope creep.**

[![Streamlit App](https://img.shields.io/badge/Streamlit%20Cloud-Live%20Application-FF4B4B?style=for-the-badge&logo=streamlit)](https://scopeguard-ai-bhadra.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/pytest-passing-10b981?style=flat&logo=pytest&logoColor=white)](tests/test_scopeguard.py)
[![License](https://img.shields.io/badge/License-MIT-6366f1?style=flat)](LICENSE)

🎈 **Live Streamlit Application:** **[https://scopeguard-ai-bhadra.streamlit.app/](https://scopeguard-ai-bhadra.streamlit.app/)**

---

## 💡 The Real Business Problem

Over **73% of digital agencies and freelance consultancies** suffer from **"Scope Creep"** — clients casually emailing or messaging on Slack:
> *"Hey! Can we quickly add Stripe checkout, user permissions, and crypto payments before Monday? It should just take an hour, right?"*

Account managers and engineers struggle because:
1. **They struggle to say "No" diplomatically** without harming high-stakes client relationships.
2. **They under-estimate the ripple effects** (frontend UI, backend APIs, data schemas, QA testing, and launch slippage).
3. **They leak thousands of dollars in unbilled labor** every month ($10,000–$30,000+ per agency).
4. **They lack instant, legally sound Addendum Agreements** that clients can sign immediately with upfront deposits.

**ScopeGuard AI solves this entire lifecycle.**

---

## ⚡ Core Capabilities & Features

### 1. 🧠 AI Scope Delta & Risk Assessment Engine
- Ingests the baseline **Statement of Work (SOW)** and the client's raw incoming request (email, Slack chat, ticket).
- Performs semantic delta classification:
  - `Minor Revision` (In-Scope, non-billable courtesy)
  - `Scope Expansion` (Billable Addendum required)
  - `Architectural Pivot` (High-Risk Scope Breach with delivery risk)
- Breaks down labor hours systematically across **Frontend**, **Backend**, **UI/UX Design**, **QA/Security**, and **Project Management**.
- Computes risk score (1–100), delivery timeline slippage (+days), and financial addendum cost.

### 2. 💬 4 Nuanced Diplomatic Client Responses
Generates instant, professionally calibrated copy ready to send back to the client:
- **🤝 Accommodating & Warm**: Enthusiastic, proposes Phase 2 or parallel addendum seamlessly.
- **🛡️ Contractually Firm**: Respectful but direct, citing sprint boundaries and signed SOW exclusions.
- **📈 Executive / ROI-Focused**: Framed for C-suite/founders; explains launch date trade-offs.
- **⚖️ Scope Trade-off / Swapping**: Proposes de-scoping lower-priority backlog items to fit within budget.

### 3. 📄 Formal Change Order Addendum Generator
- Auto-generates a legally structured, formal markdown addendum with:
  - MSA/SOW reference headers and effective dates
  - Technical deliverables & acceptance criteria
  - Exclusions and boundary conditions
  - Commercial terms (50% mobilization deposit terms)
  - Authorized signature blocks for both Agency and Client
- Includes **1-Click Markdown Download (`.md`)** ready for immediate client signature.

### 4. 📊 FinOps Token & AI Cost Tracking Architecture
- Every AI calculation tracks:
  - **Prompt Tokens**
  - **Completion Tokens**
  - **Model Tier** (e.g., `scopeguard-neural-v2`, `llama-3.3-70b`, `gpt-4o-mini`)
  - **Real USD Cost** calculated down to fractions of a cent ($0.00184 USD)
- Real-time monthly workspace token quota enforcement.
- Financial ROI metric demonstrating that **$0.18 in AI tokens recovered $14,700 in billable scope**.

### 5. 💳 Billing-Ready Architecture & Subscription Tiers
- Tiered SaaS plans:
  - **Freelance Starter** ($29/mo — 100k tokens, 1 seat)
  - **Studio Pro** ($79/mo — 500k tokens, 5 seats, priority AI engine)
  - **Agency Scale** ($199/mo — 2M tokens, unlimited seats, custom SOW clauses, BYOK)
- Interactive billing simulator with automated invoice generation and quota replenishment.

### 6. 📈 Visual SaaS Analytics & Revenue Intelligence
- Interactive visual dashboard:
  - Cumulative Recovered Revenue Timeline ($)
  - Scope Creep Category Distribution
  - Scope Creep Hours by Client Account
- Filterable Change Orders management table with lifecycle status updates (`draft` → `sent` → `approved` → `invoiced`).

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend & UI** | Streamlit 1.30+ | Clean, interactive Python data application with responsive components. |
| **Data Engine** | Pandas & SQLite | High-performance relational data processing. |
| **Database ORM** | SQLAlchemy 2.0 | Robust ACID-compliant relational persistence with WAL concurrency. |
| **AI Engine** | ScopeGuard Neural Reasoning Engine | Deterministic, multi-vector scope estimation and legal addendum generator. |
| **FinOps** | Token Counter & Pricing Engine | Exact token-level accounting and workspace quota metering. |

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Navigate
```bash
git clone https://github.com/SubhadeepBhadra/scopeguard-ai.git
cd scopeguard-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run streamlit_app.py
```
Open your browser at: **`http://localhost:8501`**

### 4. Run the Automated Test Suite
```bash
pytest tests/test_scopeguard.py -v
```

---

## 👥 Demo Account Out-of-the-Box

The application automatically seeds realistic agency data so you can test immediately:

| Profile | Email | Role | Pre-loaded Context |
|---|---|---|---|
| **Subhadeep Bhadra** | `director@scopeguard.ai` | Agency Director | 3 live client agreements, $14.7k recovered revenue, historical change orders. |

---

## 👨‍💻 Author & Attribution
Developed with pride by **Subhadeep Bhadra** ([@SubhadeepBhadra](https://github.com/SubhadeepBhadra)).  
Hosted Live on Streamlit Cloud: **[https://scopeguard-ai-bhadra.streamlit.app/](https://scopeguard-ai-bhadra.streamlit.app/)**

---

## 📄 License
MIT License. © 2026 Subhadeep Bhadra. All rights reserved.
