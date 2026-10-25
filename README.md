# 🛡️ ScopeGuard AI — Client Scope Creep & Change Order Engine
> **An AI SaaS application empowering digital agencies, software shops, and freelance consultants to protect profit margins from unbilled scope creep.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/pytest-passing-10b981?style=flat&logo=pytest&logoColor=white)](tests/test_api.py)
[![License](https://img.shields.io/badge/License-MIT-6366f1?style=flat)](LICENSE)

---

## 💡 The Real Business Problem

Over **73% of digital agencies and freelance consultancies** suffer from **"Scope Creep"** — clients casually emailing or messaging on Slack:
> *"Hey, can we quickly add Stripe checkout, user permissions, and crypto payments before Monday? It should just take an hour, right?"*

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
- Supports **1-Click Markdown Copy**, **.md File Download**, and **Print-to-PDF**.

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
- Interactive Stripe Checkout Simulator with automated invoice generation and quota replenishment.

### 6. 📈 Visual SaaS Analytics & Revenue Intelligence
- Interactive Chart.js visual dashboard:
  - Cumulative Recovered Revenue Timeline ($)
  - Scope Creep Category Distribution (Doughnut)
  - Scope Creep Hours by Client Account (Horizontal Bar)
- Filterable Change Orders management table with lifecycle status updates (`draft` → `sent` → `approved` → `invoiced`).

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend** | Python 3.11 + FastAPI + Uvicorn | Ultra-fast, async REST API with automatic OpenAPI documentation. |
| **Database** | SQLite with WAL Mode + SQLAlchemy 2.0 | Zero-config, ACID-compliant relational persistence with WAL concurrency. |
| **Frontend UI** | Semantic HTML5 + Vanilla CSS Design System | Bespoke glassmorphism dark aesthetic, CSS custom properties, zero build-step latency. |
| **Charts** | Chart.js 4.4 | Lightweight, responsive canvas data visualizations. |
| **Security** | PBKDF2-HMAC-SHA256 + Cryptographic Session Tokens | Secure password hashing with salt and bearer authentication. |
| **FinOps** | Token Counter & Pricing Engine | Exact token-level accounting and workspace quota metering. |

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Navigate
```bash
git clone <repo-url>
cd scopeguard-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Server
```bash
python run.py
```
Or with Uvicorn directly:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### 4. Run the Automated Test Suite
```bash
pytest tests/test_api.py -v
```
All 5 end-to-end integration tests will run and validate:
- System health
- Authentication & Demo accounts
- Projects CRUD & financial aggregation
- Scope analysis & FinOps token cost accounting
- Billing subscriptions & Analytics overview

---

## 🐳 Docker Deployment

To launch with Docker Compose:
```bash
docker-compose up --build -d
```
The application will be live at `http://localhost:8000`.

---

## 👥 Demo Accounts Available Out-of-the-Box

The application automatically seeds realistic agency data so you can test immediately:

| Profile | Email | Password | Role | Pre-loaded Context |
|---|---|---|---|---|
| **Elena Rostova** | `director@scopeguard.ai` | `password123` | Agency Director | 3 live client agreements, $14.7k recovered revenue, historical change orders. |
| **Marcus Chen** | `freelancer@scopeguard.ai` | `password123` | Solo Freelancer | Clean freelance slate with Starter plan. |

*You can toggle between demo roles directly using the top-bar dropdown in the UI!*

---

## 📑 API Endpoints Summary

- `POST /api/auth/register` — Register new studio account
- `POST /api/auth/login` — Sign in
- `POST /api/auth/demo-login` — 1-click evaluation access
- `GET /api/projects` — List client projects with financial rollups
- `POST /api/projects` — Create new client Statement of Work
- `POST /api/scope/analyze` — Run AI scope analysis and generate change order
- `GET /api/scope/change-orders` — List and filter change orders
- `PATCH /api/scope/change-orders/{id}/status` — Update approval status
- `GET /api/scope/change-orders/{id}/export` — Download raw addendum markdown
- `GET /api/billing/plans` — List subscription plans
- `POST /api/billing/subscribe` — Upgrade/downgrade subscription
- `GET /api/billing/usage` — Workspace FinOps token consumption
- `GET /api/analytics/overview` — SaaS metrics, ROI multiplier, and chart series

---

## 📄 License
MIT License. Created for Challenge 1: AI SaaS MVP.
