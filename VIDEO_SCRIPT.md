# 🎬 ScopeGuard AI — Screen-Sharing Video Walkthrough Script
**Presenter:** Subhadeep Bhadra (Founder / Lead Engineer)  
**Target Duration:** ~5 to 6 minutes  
**Format:** Screen Recording with Picture-in-Picture Webcam (or Voiceover + Screen Capture)  
**Apps to Share:** Browser window open at `http://127.0.0.1:8000` (or the live public URL) and Streamlit at `http://localhost:8501`.

---

## ⏱️ Timeline & Scene Overview

| Time | Section | Screen Action |
|---|---|---|
| **0:00 – 0:45** | **The Hook & The $30k Problem** | Camera on you / Title slide, then switch to Dashboard |
| **0:45 – 1:30** | **Executive Dashboard & ROI** | Highlight Recovered Revenue ($14,700), hours saved, FinOps ROI |
| **1:30 – 3:15** | **The Core Demo: Scope Studio** | Run AI analysis on real client request, show breakdown & 4 tones |
| **3:15 – 4:00** | **Contract Addendum & Lifecycle** | Markdown contract view, export, status update to Approved |
| **4:00 – 4:45** | **FinOps Analytics & Unit Economics** | Chart.js / Streamlit charts showing token costs vs revenue |
| **4:45 – 5:30** | **Billing Architecture & SaaS Plans** | Stripe simulator, 3 tiers, and automated invoices |
| **5:30 – 6:00** | **Architecture, Streamlit & Conclusion** | Dual-stack (FastAPI + Streamlit), GitHub repo, wrap-up |

---

## 🎙️ Detailed Scene-by-Scene Script

### Scene 1: The Hook & The Problem (0:00 – 0:45)
**Visual Cue:**
- *Start with your camera full-screen, or show the browser on the ScopeGuard AI Dashboard with the glowing shield logo.*

**Spoken Narration:**
> "Hey everyone, my name is **Subhadeep Bhadra**, and today I’m excited to show you **ScopeGuard AI** — an AI SaaS platform built to solve one of the most painful, expensive problems in the software industry: **unbilled client scope creep**.
>
> If you've ever worked at a digital agency, software house, or as a freelance developer, you’ve definitely lived through this scenario: You sign a fixed-scope contract, and two weeks in, the client sends a casual Slack message:
> *'Hey! Can we quickly add Stripe payments, multi-currency checkout, and crypto before launch? It should just take an hour, right?'*
>
> Most developers and account managers don't know how to push back without souring the relationship, so they end up eating dozens of unpaid hours. Over 73% of agencies leak between $10,000 to $30,000 every single month from unbilled revisions.
>
> ScopeGuard AI completely eliminates this problem. Let me show you how it works in action."

---

### Scene 2: The Executive Dashboard (0:45 – 1:30)
**Visual Cue:**
- *Share full screen at `http://127.0.0.1:8000/#dashboard`. Move your mouse smoothly over the top 4 metric cards.*

**Spoken Narration:**
> "Here on the main dashboard, you immediately see the business impact. 
> 
> As an agency director, I can instantly see:
> - **$14,700 in Recovered Revenue** that would have otherwise slipped through as free labor.
> - **97.0 Protected Creep Hours** saved across our engineering and QA teams.
> - An **83% Addendum Approval Rate**, meaning clients actually sign off on our change orders because of how professionally they're framed.
> - And our **FinOps AI ROI Multiplier of 80,450x** — showing that just a fraction of a dollar in AI inference tokens translated into nearly fifteen thousand dollars of billable client work.
>
> Down below, we have our active client agreements — like the *FinTech Dashboard App* and *Headless E-Commerce Storefront* — with their baseline Statement of Work (SOW) deliverables locked into the system."

---

### Scene 3: The Core Magic — AI Scope Studio (1:30 – 3:15)
**Visual Cue:**
- *Click on **'⚡ Scope Studio'** in the navigation bar. The Scope Analyzer view slides smoothly into place.*
- *Select **'FinTech Dashboard & Portfolio App'** from the dropdown.*
- *Click the preset chip **'💳 Stripe & Crypto Payment'** to auto-populate the request.*
- *Click the glowing button **'⚡ Analyze Scope & Generate Addendum'**.*

**Spoken Narration:**
> "Now let's see the core AI engine. 
> 
> Suppose a client on our FinTech project sends this message:
> *'Hey Subhadeep! Can we quickly allow users to deposit funds directly via Stripe in USD and EUR? Should just take an afternoon right? Also let us know if Bitcoin deposits are easy to toggle.'*
> 
> Instead of arguing or guessing hours, I just paste the request right here and click **Analyze Scope & Generate Addendum**.
>
> *(Wait 1-2 seconds as the analysis completes and the results section scrolls into view)*
>
> Look at what the engine just did in under two seconds:
> 1. **Classification & Risk Severity:** It classified this as a **Scope Expansion** with a risk score of **72/100 (High Risk)** because payment gateways require webhook reconciliation, compliance, and ledger audits.
> 2. **Labor Hours Breakdown:** It estimated **33 billable engineering hours** — breaking it down accurately across Frontend (8 hrs), Backend (14 hrs), QA Testing (6 hrs), and PM (3 hrs).
> 3. **Financial Valuation:** At our studio rate of $150/hr, this generates a **$4,950 billable Change Order** and extends the delivery timeline by **+6 business days**.
> 4. **FinOps Token Ticker:** Right here, you can see our built-in FinOps telemetry. It consumed exactly 1,840 tokens, costing our platform **$0.00184 USD** — fraction of a cent."

---

### Scene 4: Diplomatic Client Responses & Legal Addendum (3:15 – 4:00)
**Visual Cue:**
- *Click through the tabs: **'🤝 Accommodating'**, **'🛡️ Contractually Firm'**, **'📈 Executive / ROI'**, and **'⚖️ Scope Trade-off'**.*
- *Click **'📋 Copy to Clipboard'** (toast appears: 'Diplomatic response copied to clipboard!').*
- *Scroll down to the **'📄 Formal Change Order Addendum'** preview.*

**Spoken Narration:**
> "Here’s where ScopeGuard AI really shines: the client communication. Saying 'no' is hard, so ScopeGuard generates **four distinct diplomatic response tones**:
> - **Accommodating:** Enthusiastic and friendly, positioning this as an exciting Phase 2 addendum.
> - **Contractually Firm:** Direct and respectful, referencing the signed SOW boundary.
> - **Executive / ROI-Focused:** Written for founders and CEOs, laying out the timeline trade-off.
> - **Scope Trade-off:** Offering to swap out a lower-priority feature so they stay within their existing budget.
>
> I can simply click **Copy to Clipboard** — see the instant notification — and paste it right into Slack or Gmail.
>
> And underneath, it auto-generates a complete, legally sound **Change Order Addendum Agreement** with deliverable specs, schedule adjustments, a mandatory 50% mobilization deposit clause, and authorized signature blocks. You can download the markdown file or print it directly to PDF."

---

### Scene 5: Change Orders Lifecycle & FinOps Analytics (4:00 – 4:45)
**Visual Cue:**
- *Click on **'📑 Change Orders'** in the navigation. Show the table.*
- *Change a status dropdown from 'Draft' to 'Approved'.*
- *Click on **'📈 FinOps Analytics'** in the navigation bar to display the interactive Chart.js graphs.*

**Spoken Narration:**
> "In the **Change Orders** tab, account managers can track all client revision requests in one place. When a client signs off, we update the status to **Approved** or **Invoiced**, which automatically feeds into our revenue reports.
>
> Moving over to **FinOps Analytics**:
> Here we have live interactive charts powered by Chart.js. 
> - On the left, we track our **Cumulative Recovered Revenue Growth** month-over-month.
> - On the right, we see the distribution of creep by risk category — distinguishing between minor revisions, scope expansions, and high-risk architectural pivots.
> - Below, we see which client accounts generate the most unbilled change requests, giving agency leadership data-driven leverage during contract renewal discussions."

---

### Scene 6: Billing Architecture & Stripe Simulation (4:45 – 5:30)
**Visual Cue:**
- *Click on **'💳 Subscription & Plans'**.*
- *Show the 3 cards: Freelance Starter ($29), Studio Pro ($79), Agency Scale ($199).*
- *Click **'Upgrade to Agency'** on the Agency Scale card.*
- *In the Stripe checkout modal, click **'Confirm & Authorize Payment'**.*

**Spoken Narration:**
> "ScopeGuard AI is built on a production-ready SaaS billing architecture:
> - **Freelance Starter ($29/mo)** with 100k tokens.
> - **Studio Pro ($79/mo)** with 500k tokens and team seats.
> - **Agency Scale ($199/mo)** with 2 million tokens and Bring-Your-Own-Key (BYOK) support.
>
> We’ve integrated a sandbox Stripe checkout workflow. When I click **Upgrade to Agency**, authorize the test payment, the subscription activates immediately, issues a paid invoice receipt, and refreshes the agency's token quota in real time."

---

### Scene 7: Streamlit Edition & Cloud Deployment (5:30 – 6:15)
**Visual Cue:**
- *Switch browser tab to the Streamlit app at `http://localhost:8501` (or the public tunnel).*
- *Briefly scroll through the Streamlit interface demonstrating the same live database and features.*
- *Switch to the GitHub repository at `https://github.com/SubhadeepBhadra/scopeguard-ai`.*

**Spoken Narration:**
> "To make this project as accessible as possible, I built it with a dual-frontend architecture:
> 1. A custom, ultra-fast **FastAPI and modern glassmorphic web application**.
> 2. A dedicated **Streamlit application (`streamlit_app.py`)** that delivers the entire workflow with native Python data components, ready for 1-click deployment on Streamlit Community Cloud.
>
> The entire codebase is open-source, tested with an automated `pytest` suite, dockerized with `docker-compose`, and live on GitHub at `SubhadeepBhadra/scopeguard-ai`.
>
> ScopeGuard AI turns scope creep from an agency's biggest profit leak into its most reliable revenue stream.
>
> Thank you for watching, and feel free to check out the live demo links in the description below!"

---

## 💡 Tips for Recording

1. **Screen Resolution:** Record at 1080p (1920x1080) for crisp typography and clean card borders.
2. **Zoom Level:** Set browser zoom to 100% or 110% so the KPI numbers and badges are punchy and easily readable on mobile screens.
3. **Pacing:** Pause for 1 second after clicking buttons (e.g. after clicking *Analyze Scope*) so viewers can watch the live UI transition smoothly.
4. **Mouse Movement:** Move the cursor deliberately to guide the viewer's eye to key areas (e.g., the risk score, the token ticker, the copy button).
