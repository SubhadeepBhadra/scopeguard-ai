import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_demo_login():
    res = client.post("/api/auth/demo-login", json={"role": "director"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["email"] == "director@scopeguard.ai"
    assert data["user"]["role"] == "director"

def test_projects_flow():
    # Login as director
    login_res = client.post("/api/auth/demo-login", json={"role": "director"})
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List projects
    res = client.get("/api/projects", headers=headers)
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) >= 3
    assert any("FinTech" in p["project_name"] for p in projects)

    # Create new project
    create_res = client.post("/api/projects", headers=headers, json={
        "project_name": "SaaS Marketing Website Redesign",
        "client_name": "Acme Ventures",
        "baseline_sow": "Design and build 4 marketing pages with Webflow or React.",
        "hourly_rate": 140.0,
        "currency": "USD"
    })
    assert create_res.status_code == 201
    created_id = create_res.json()["project"]["id"]
    assert created_id is not None

def test_scope_analysis_and_finops():
    login_res = client.post("/api/auth/demo-login", json={"role": "director"})
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Run AI Scope Analysis on a new request
    payload = {
        "project_name": "SaaS Marketing Website",
        "client_name": "Acme Ventures",
        "baseline_sow": "Design and build 4 marketing pages with Webflow or React.",
        "client_request_raw": "Hey! Can we quickly integrate a custom Stripe payment checkout with customer portal and automated invoicing before launch?",
        "hourly_rate": 150.0,
        "currency": "USD"
    }
    analyze_res = client.post("/api/scope/analyze", headers=headers, json=payload)
    assert analyze_res.status_code == 200
    data = analyze_res.json()

    assert data["status"] == "success"
    analysis = data["analysis"]
    assert analysis["category"] in ["Scope Expansion", "Architectural Pivot"]
    assert analysis["estimated_hours"] > 0
    assert analysis["billable_amount"] > 0
    assert "accommodating" in analysis["diplomatic_responses"]
    assert "firm" in analysis["diplomatic_responses"]
    assert "CHANGE ORDER ADDENDUM" in analysis["agreement_markdown"]

    # Verify FinOps Token Accounting
    finops = data["finops"]
    assert finops["prompt_tokens"] > 0
    assert finops["completion_tokens"] > 0
    assert finops["total_tokens"] > 0
    assert finops["ai_cost_usd"] > 0

    co_id = data["change_order_id"]

    # Update status to approved
    status_res = client.patch(f"/api/scope/change-orders/{co_id}/status", headers=headers, json={"status": "approved"})
    assert status_res.status_code == 200

    # Export markdown
    export_res = client.get(f"/api/scope/change-orders/{co_id}/export", headers=headers)
    assert export_res.status_code == 200
    assert "CHANGE ORDER" in export_res.text

def test_billing_and_analytics():
    login_res = client.post("/api/auth/demo-login", json={"role": "director"})
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Plans
    plans_res = client.get("/api/billing/plans")
    assert plans_res.status_code == 200
    assert len(plans_res.json()) == 3

    # Usage
    usage_res = client.get("/api/billing/usage", headers=headers)
    assert usage_res.status_code == 200
    assert "monthly_token_quota" in usage_res.json()

    # Analytics overview
    analytics_res = client.get("/api/analytics/overview", headers=headers)
    assert analytics_res.status_code == 200
    stats = analytics_res.json()
    assert "summary" in stats
    assert stats["summary"]["recovered_revenue"] > 0
    assert stats["summary"]["total_ai_cost_usd"] >= 0
    assert "category_distribution" in stats
    assert "monthly_trend" in stats
