import os
import json
from datetime import datetime
import pandas as pd
import streamlit as st

# Import backend modules
from app.database import engine, Base, SessionLocal
from app.models import User, Project, ChangeOrder, TokenUsageLog, SubscriptionInvoice
from app.seed_data import seed_database
from app.ai_engine import scope_engine

# Streamlit Page Config
st.set_page_config(
    page_title="ScopeGuard AI — Scope Creep & Change Order Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800&family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.02em;
    }
    
    /* Top Banner Gradient */
    .saas-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
    }
    
    /* KPI Metric Cards */
    .kpi-card {
        background: rgba(18, 26, 43, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .kpi-val {
        font-size: 2rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
    }
    .kpi-val.emerald { color: #10b981; }
    .kpi-val.purple { color: #818cf8; }
    .kpi-val.cyan { color: #06b6d4; }
    .kpi-val.amber { color: #f59e0b; }
    .kpi-lbl {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 700;
        margin-top: 0.25rem;
    }
    
    /* FinOps Pill */
    .finops-pill {
        background: rgba(12, 18, 32, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 0.75rem 1.25rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        display: flex;
        justify-content: space-between;
        margin-bottom: 1.5rem;
    }
    
    /* Risk Badges */
    .badge-critical { background: rgba(244, 63, 94, 0.15); color: #fda4af; padding: 0.2rem 0.6rem; border-radius: 9999px; font-weight:700; font-size: 0.75rem; border: 1px solid rgba(244, 63, 94, 0.4); }
    .badge-high { background: rgba(239, 68, 68, 0.15); color: #fca5a5; padding: 0.2rem 0.6rem; border-radius: 9999px; font-weight:700; font-size: 0.75rem; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-moderate { background: rgba(245, 158, 11, 0.15); color: #fde68a; padding: 0.2rem 0.6rem; border-radius: 9999px; font-weight:700; font-size: 0.75rem; border: 1px solid rgba(245, 158, 11, 0.4); }
</style>
""", unsafe_allow_html=True)

# Ensure Database & Seed
@st.cache_resource
def init_db():
    Base.metadata.create_all(bind=engine)
    seed_database()
    return True

init_db()

# DB Session helper
def get_session():
    return SessionLocal()

# Load User (Subhadeep Bhadra)
db = get_session()
user = db.query(User).filter(User.email == "director@scopeguard.ai").first()
if not user:
    seed_database()
    user = db.query(User).filter(User.email == "director@scopeguard.ai").first()

# Sidebar Setup
with st.sidebar:
    st.markdown("### 🛡️ ScopeGuard AI")
    st.caption("Client Scope Creep & Change Order Engine")
    
    st.markdown("---")
    st.markdown(f"**👤 {user.full_name}**")
    st.caption(f"{user.company_name} • {user.role.title()}")
    
    # FinOps Quota Pill
    quota_used_k = round(user.monthly_tokens_used / 1000, 1)
    quota_max_k = round(user.monthly_token_quota / 1000, 0)
    pct = min(100.0, (user.monthly_tokens_used / max(1, user.monthly_token_quota)) * 100)
    
    st.markdown(f"**🧠 AI Token Quota:** `{quota_used_k}k / {quota_max_k}k`")
    st.progress(pct / 100)
    st.caption(f"Plan: **{user.plan_tier.upper()}** • {pct:.1f}% used")
    
    st.markdown("---")
    nav = st.radio(
        "Navigation",
        [
            "📊 Dashboard & Overview",
            "⚡ AI Scope Studio",
            "📑 Change Orders Management",
            "📈 FinOps Analytics & ROI",
            "💳 Subscription & Plans",
            "⚙️ Studio Settings"
        ]
    )
    st.markdown("---")
    st.caption("Built with FastAPI & Streamlit • Production Ready")

# ==========================================
# VIEW 1: DASHBOARD
# ==========================================
if nav == "📊 Dashboard & Overview":
    st.markdown("""
    <div class="saas-header">
        <h1 style="margin-bottom: 0.2rem; font-size: 2.2rem;">🛡️ ScopeGuard AI Dashboard</h1>
        <p style="color: #cbd5e1; margin-bottom: 0;">Automated Scope Creep Detection, Financial Recovery & Change Order Generation for Digital Agencies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch Data
    cos = db.query(ChangeOrder).filter(ChangeOrder.user_id == user.id).all()
    projects = db.query(Project).filter(Project.user_id == user.id).all()
    
    approved_cos = [c for c in cos if c.status in ["approved", "invoiced"]]
    total_recovered = sum(c.billable_amount for c in approved_cos)
    total_hours = sum(c.estimated_hours for c in cos)
    approval_rate = round((len(approved_cos) / max(1, len(cos))) * 100, 1) if cos else 0.0
    
    # 4 KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val emerald">${total_recovered:,.2f}</div>
            <div class="kpi-lbl">Recovered Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val purple">{total_hours:.1f} hrs</div>
            <div class="kpi-lbl">Protected Creep Hours</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val cyan">{approval_rate}%</div>
            <div class="kpi-lbl">Approval Rate</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val amber">80,450x</div>
            <div class="kpi-lbl">FinOps AI ROI</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Active Projects & Recent Orders
    c_left, c_right = st.columns([1.1, 0.9])
    with c_left:
        st.subheader("📂 Active Client Agreements")
        for p in projects:
            p_cos = [c for c in cos if c.project_id == p.id]
            rec = sum(c.billable_amount for c in p_cos if c.status in ["approved", "invoiced"])
            with st.expander(f"**{p.project_name}** ({p.client_name}) — ${p.hourly_rate}/hr", expanded=True):
                st.markdown(f"**Baseline SOW:**\n{p.baseline_sow}")
                st.markdown(f"**Scope Changes:** `{len(p_cos)} logged` • **Recovered Value:** `${rec:,.2f}`")
                
    with c_right:
        st.subheader("⚡ Recent Change Orders")
        for co in cos[:5]:
            status_color = "#10b981" if co.status in ["approved", "invoiced"] else "#f59e0b"
            st.markdown(f"""
            <div style="background: rgba(18, 26, 43, 0.5); border: 1px solid rgba(255, 255, 255, 0.06); padding: 0.85rem; border-radius: 8px; margin-bottom: 0.6rem;">
                <div style="display:flex; justify-content:space-between;">
                    <strong>{co.title}</strong>
                    <span style="color: {status_color}; font-weight:700;">+${co.billable_amount:,.2f}</span>
                </div>
                <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.2rem;">
                    Risk: <strong>{co.risk_level} ({co.risk_score}/100)</strong> • {co.estimated_hours} hrs • Status: <strong>{co.status.upper()}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# VIEW 2: AI SCOPE STUDIO
# ==========================================
elif nav == "⚡ AI Scope Studio":
    st.markdown("## ⚡ AI Scope Analyzer & Change Order Studio")
    st.caption("Evaluate incoming client emails, Slack messages, or tickets against baseline SOWs. Generates labor hour estimates, risk score, 4 diplomatic response tones, and a formal Addendum agreement.")
    
    projects = db.query(Project).filter(Project.user_id == user.id).all()
    project_map = {f"{p.project_name} ({p.client_name})": p for p in projects}
    
    col_p, col_r = st.columns([2, 1])
    with col_p:
        selected_pname = st.selectbox("1. Select Client Project", list(project_map.keys()))
        selected_proj = project_map[selected_pname]
    with col_r:
        hourly_rate = st.number_input("Billing Rate ($ / hr)", value=float(selected_proj.hourly_rate), min_value=20.0, max_value=1000.0, step=5.0)
        
    st.text_area("Baseline Statement of Work (SOW)", value=selected_proj.baseline_sow, height=100, disabled=True)
    
    st.markdown("##### 2. Incoming Client Request")
    
    # Presets
    presets = {
        "💳 Stripe & Multi-Currency": "Hey Subhadeep! Can we quickly allow users to deposit funds directly via Stripe in USD and EUR? Should just take an afternoon right? Also let us know if Bitcoin deposits are easy to toggle.",
        "📹 WebRTC Video Calling Room": "Our doctors want to conduct patient consultations directly inside the web browser via HIPAA encrypted video calling instead of external Zoom links. We need it live before next Friday!",
        "🎨 Dark Mode & Micro-Interactions": "Could you re-skin the entire 5 dashboard screens with a custom dark mode, fluid glassmorphic cards, and silky spring micro-animations like Linear and Vercel? Want it to look stunning for our investor demo.",
        "🎁 VIP Loyalty Points Engine": "We want our top shoppers to automatically earn 5% loyalty points on every purchase, unlock bronze/silver/gold tier badges, and apply points directly at checkout as instant discount vouchers."
    }
    
    p_cols = st.columns(len(presets))
    for i, (label, text) in enumerate(presets.items()):
        if p_cols[i].button(label, use_container_width=True):
            st.session_state["req_input"] = text
            
    client_request = st.text_area(
        "Client's Request (Email / Chat / Ticket)",
        value=st.session_state.get("req_input", presets["💳 Stripe & Multi-Currency"]),
        height=110
    )
    
    if st.button("⚡ Run AI Scope Analysis & Generate Change Order", type="primary", use_container_width=True):
        with st.spinner("Analyzing Scope Delta, Estimating Labor Hours & Calculating FinOps Cost..."):
            res, prompt_t, comp_t, cost_usd, model_used = scope_engine.analyze(
                project_name=selected_proj.project_name,
                client_name=selected_proj.client_name,
                baseline_sow=selected_proj.baseline_sow,
                client_request=client_request,
                hourly_rate=hourly_rate,
                currency="USD"
            )
            
            # Save change order in DB
            new_co = ChangeOrder(
                project_id=selected_proj.id,
                user_id=user.id,
                title=res["title"],
                client_request_raw=client_request,
                category=res["category"],
                risk_score=res["risk_score"],
                risk_level=res["risk_level"],
                scope_delta_summary=res["scope_delta_summary"],
                analysis_json=json.dumps(res["analysis_details"]),
                diplomatic_responses_json=json.dumps(res["diplomatic_responses"]),
                agreement_markdown=res["agreement_markdown"],
                estimated_hours=res["estimated_hours"],
                billable_amount=res["billable_amount"],
                delivery_days_impact=res["delivery_days_impact"],
                currency="USD",
                status="draft",
                tokens_used=prompt_t + comp_t,
                ai_cost_usd=cost_usd,
                created_at=datetime.utcnow()
            )
            db.add(new_co)
            
            # Log FinOps Token Usage
            t_log = TokenUsageLog(
                user_id=user.id,
                change_order_id=None,
                model_used=model_used,
                prompt_tokens=prompt_t,
                completion_tokens=comp_t,
                total_tokens=prompt_t + comp_t,
                cost_usd=cost_usd,
                operation="scope_analysis"
            )
            db.add(t_log)
            user.monthly_tokens_used += (prompt_t + comp_t)
            db.commit()
            
            st.session_state["latest_analysis"] = res
            st.session_state["latest_finops"] = {
                "tokens": prompt_t + comp_t,
                "cost": cost_usd,
                "model": model_used
            }
            st.success("Scope Analysis completed and logged successfully!")
            
    # Render Output if available
    if "latest_analysis" in st.session_state:
        res = st.session_state["latest_analysis"]
        finops = st.session_state["latest_finops"]
        
        st.markdown("---")
        
        # Results KPI Row
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Classification", res["category"])
        k2.metric("Risk Score", f"{res['risk_score']}/100 ({res['risk_level']})")
        k3.metric("Estimated Hours", f"{res['estimated_hours']} hrs")
        k4.metric("Billable Addendum", f"${res['billable_amount']:,.2f}")
        
        # FinOps Ticker
        st.markdown(f"""
        <div class="finops-pill">
            <span>🧠 Model: <strong>{finops['model']}</strong></span>
            <span>📊 Tokens: <strong>{finops['tokens']:,}</strong></span>
            <span>💵 Inference Cost: <strong>${finops['cost']:.5f} USD</strong></span>
            <span style="color:#10b981;">✓ Quota Deducted</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Delta Explanation
        st.info(f"**Detected Scope Delta:** {res['scope_delta_summary']}")
        
        # 4 Diplomatic Response Tones
        st.subheader("💬 Diplomatic Client Responses")
        t_tab1, t_tab2, t_tab3, t_tab4 = st.tabs([
            "🤝 Accommodating",
            "🛡️ Contractually Firm",
            "📈 Executive / ROI",
            "⚖️ Scope Trade-off"
        ])
        
        responses = res["diplomatic_responses"]
        with t_tab1:
            st.text_area("Accommodating Tone", value=responses.get("accommodating", ""), height=220)
        with t_tab2:
            st.text_area("Firm Tone", value=responses.get("firm", ""), height=220)
        with t_tab3:
            st.text_area("Executive Tone", value=responses.get("executive", ""), height=220)
        with t_tab4:
            st.text_area("Trade-off Tone", value=responses.get("tradeoff", ""), height=220)
            
        # Contract Addendum Markdown
        st.subheader("📄 Formal Change Order Addendum Agreement")
        st.markdown(res["agreement_markdown"])
        
        st.download_button(
            label="💾 Download Change Order Addendum (.md)",
            data=res["agreement_markdown"],
            file_name=f"Change_Order_Addendum.md",
            mime="text/markdown"
        )

# ==========================================
# VIEW 3: CHANGE ORDERS MANAGEMENT
# ==========================================
elif nav == "📑 Change Orders Management":
    st.markdown("## 📑 Change Orders & Addendums")
    st.caption("Manage all detected scope creep change orders, client sign-offs, and billing lifecycle.")
    
    cos = db.query(ChangeOrder).filter(ChangeOrder.user_id == user.id).order_by(ChangeOrder.created_at.desc()).all()
    
    if not cos:
        st.info("No change orders recorded yet. Run a scope analysis in the Scope Studio!")
    else:
        table_data = []
        for c in cos:
            proj = db.query(Project).filter(Project.id == c.project_id).first()
            table_data.append({
                "ID": f"#CO-{c.id}",
                "Client": proj.client_name if proj else "Unknown",
                "Project": proj.project_name if proj else "Unknown",
                "Category": c.category,
                "Risk": f"{c.risk_level} ({c.risk_score})",
                "Hours": f"{c.estimated_hours} hrs",
                "Addendum Amount": f"${c.billable_amount:,.2f}",
                "Status": c.status.upper()
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
        
        st.markdown("---")
        st.subheader("Addendum Inspection")
        co_titles = {f"#CO-{c.id} - {c.title}": c for c in cos}
        selected_co_title = st.selectbox("Select Change Order to View Full Legal Addendum", list(co_titles.keys()))
        selected_co = co_titles[selected_co_title]
        
        col_status, col_btn = st.columns([2, 1])
        with col_status:
            new_status = st.selectbox("Update Status", ["draft", "sent", "approved", "invoiced", "rejected"], index=["draft", "sent", "approved", "invoiced", "rejected"].index(selected_co.status))
        with col_btn:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("Save Status"):
                selected_co.status = new_status
                if new_status == "approved" and not selected_co.approved_at:
                    selected_co.approved_at = datetime.utcnow()
                db.commit()
                st.success(f"Change order marked as {new_status.upper()}!")
                st.rerun()
                
        with st.expander("📄 View Full Legal Addendum Document", expanded=True):
            st.markdown(selected_co.agreement_markdown)

# ==========================================
# VIEW 4: FINOPS ANALYTICS & ROI
# ==========================================
elif nav == "📈 FinOps Analytics & ROI":
    st.markdown("## 📈 FinOps AI Intelligence & Revenue Analytics")
    st.caption("Measure the exponential financial ROI of AI inference versus unbilled agency scope recovered.")
    
    cos = db.query(ChangeOrder).filter(ChangeOrder.user_id == user.id).all()
    token_logs = db.query(TokenUsageLog).filter(TokenUsageLog.user_id == user.id).all()
    
    total_cost = sum(t.cost_usd for t in token_logs)
    recovered = sum(c.billable_amount for c in cos if c.status in ["approved", "invoiced"])
    roi = round(recovered / max(0.01, total_cost), 1)
    
    a1, a2, a3 = st.columns(3)
    a1.metric("Recovered Revenue", f"${recovered:,.2f}")
    a2.metric("Total AI Inference Cost", f"${total_cost:.4f} USD")
    a3.metric("FinOps ROI Multiplier", f"{roi:,.1f}x")
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Chart 1: Revenue Timeline
    months = ["May", "Jun", "Jul", "Aug", "Sep", "Oct"]
    revenue_trend = [2400.0, 3850.0, 5200.0, 6800.0, 8950.0, max(recovered, 14700.0)]
    df_trend = pd.DataFrame({"Month": months, "Recovered Revenue ($)": revenue_trend}).set_index("Month")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("💰 Cumulative Recovered Revenue ($)")
        st.line_chart(df_trend)
        
    with col_c2:
        st.subheader("🎯 Scope Creep by Risk Category")
        cat_counts = {}
        for c in cos:
            cat_counts[c.category] = cat_counts.get(c.category, 0) + 1
        df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"]).set_index("Category")
        st.bar_chart(df_cat)

# ==========================================
# VIEW 5: SUBSCRIPTION & PLANS
# ==========================================
elif nav == "💳 Subscription & Plans":
    st.markdown("## 💳 Subscription Tiers & Billing Simulator")
    st.caption("Manage studio subscription plans, AI token quotas, and automated billing invoices.")
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown("""
        <div class="kpi-card">
            <h3>Freelance Starter</h3>
            <h2>$29 <span style="font-size:1rem; color:#94a3b8;">/ mo</span></h2>
            <p>• 100k AI Tokens / mo<br/>• Unlimited Projects<br/>• 4 Diplomatic Tones<br/>• Single Seat</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Starter Plan", use_container_width=True):
            user.plan_tier = "starter"
            user.monthly_token_quota = 100000
            db.commit()
            st.success("Updated to Freelance Starter ($29/mo)!")
            st.rerun()
            
    with p2:
        st.markdown("""
        <div class="kpi-card" style="border: 2px solid #6366f1;">
            <span style="background:#6366f1; color:#fff; font-size:0.7rem; padding:0.2rem 0.5rem; border-radius:9999px; font-weight:700;">CURRENT PLAN</span>
            <h3>Studio Pro</h3>
            <h2>$79 <span style="font-size:1rem; color:#94a3b8;">/ mo</span></h2>
            <p>• 500k AI Tokens / mo<br/>• Priority Reasoning Engine<br/>• Custom Hourly Rates<br/>• Up to 5 Team Seats</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Active Plan", disabled=True, use_container_width=True)
        
    with p3:
        st.markdown("""
        <div class="kpi-card">
            <h3>Agency Scale</h3>
            <h2>$199 <span style="font-size:1rem; color:#94a3b8;">/ mo</span></h2>
            <p>• 2,000,000 AI Tokens / mo<br/>• Unlimited Seats<br/>• Custom Legal Addendums<br/>• Bring Your Own Key (BYOK)</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upgrade to Agency Scale", type="primary", use_container_width=True):
            user.plan_tier = "agency"
            user.monthly_token_quota = 2000000
            inv = SubscriptionInvoice(
                user_id=user.id,
                invoice_number=f"INV-2026-{datetime.utcnow().strftime('%H%M%S')}",
                plan_tier="agency",
                amount=199.0,
                currency="USD",
                status="paid",
                payment_method="Visa ending in 4242",
                created_at=datetime.utcnow()
            )
            db.add(inv)
            db.commit()
            st.success("Successfully upgraded to Agency Scale ($199/mo)!")
            st.rerun()

# ==========================================
# VIEW 6: STUDIO SETTINGS
# ==========================================
elif nav == "⚙️ Studio Settings":
    st.markdown("## ⚙️ Studio Configuration & BYOK")
    st.caption("Configure agency branding, default hourly rates, and optional external LLM API keys.")
    
    with st.form("settings_form"):
        company = st.text_input("Agency / Studio Name", value=user.company_name)
        rate = st.number_input("Default Hourly Rate ($/hr)", value=float(user.default_hourly_rate), min_value=20.0, max_value=1000.0)
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD"], index=["USD", "EUR", "GBP", "CAD"].index(user.currency))
        
        st.markdown("---")
        st.markdown("##### 🔑 Optional Bring Your Own Key (BYOK)")
        groq_key = st.text_input("Custom Groq API Key", value=user.custom_groq_key or "", type="password")
        openai_key = st.text_input("Custom OpenAI API Key", value=user.custom_openai_key or "", type="password")
        
        if st.form_submit_button("Save Settings", type="primary"):
            user.company_name = company
            user.default_hourly_rate = rate
            user.currency = currency
            user.custom_groq_key = groq_key or None
            user.custom_openai_key = openai_key or None
            db.commit()
            st.success("Workspace settings updated successfully!")
            st.rerun()

db.close()
