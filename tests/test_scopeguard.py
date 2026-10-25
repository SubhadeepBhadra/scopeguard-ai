import pytest
from app.database import engine, Base, SessionLocal
from app.models import User, Project, ChangeOrder, TokenUsageLog, SubscriptionInvoice
from app.seed_data import seed_database
from app.ai_engine import scope_engine

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    seed_database()
    db = SessionLocal()
    yield db
    db.close()

def test_database_and_user_seed(db_session):
    user = db_session.query(User).filter(User.email == "director@scopeguard.ai").first()
    assert user is not None
    assert user.full_name == "Subhadeep Bhadra"
    assert user.role == "director"
    assert user.plan_tier in ["starter", "pro", "agency"]
    assert user.monthly_token_quota > 0

def test_projects_seeded(db_session):
    projects = db_session.query(Project).all()
    assert len(projects) >= 3
    fintech_proj = next((p for p in projects if "FinTech" in p.project_name), None)
    assert fintech_proj is not None
    assert fintech_proj.hourly_rate == 150.0

def test_ai_scope_engine_analysis():
    # Test Scope Creep Analysis on a real request
    project_name = "FinTech Dashboard & Portfolio App"
    client_name = "Acme Global Financial"
    baseline_sow = "5-page financial dashboard with Plaid read-only balance viewer and user authentication."
    client_request = "Can we quickly add Stripe checkout and multi-currency conversion before next Monday?"
    
    analysis, prompt_tokens, comp_tokens, cost_usd, model_used = scope_engine.analyze(
        project_name=project_name,
        client_name=client_name,
        baseline_sow=baseline_sow,
        client_request=client_request,
        hourly_rate=150.0,
        currency="USD"
    )
    
    assert analysis["category"] in ["Scope Expansion", "Architectural Pivot"]
    assert analysis["risk_score"] > 0
    assert analysis["estimated_hours"] > 0
    assert analysis["billable_amount"] > 0
    
    # Verify 4 diplomatic responses
    responses = analysis["diplomatic_responses"]
    assert "accommodating" in responses
    assert "firm" in responses
    assert "executive" in responses
    assert "tradeoff" in responses
    
    # Verify legal addendum
    assert "CHANGE ORDER ADDENDUM" in analysis["agreement_markdown"]
    
    # Verify FinOps telemetry
    assert prompt_tokens > 0
    assert comp_tokens > 0
    assert cost_usd > 0
    assert model_used == "scopeguard-neural-v2"

def test_change_order_creation_and_status(db_session):
    user = db_session.query(User).filter(User.email == "director@scopeguard.ai").first()
    proj = db_session.query(Project).filter(Project.user_id == user.id).first()
    
    co = ChangeOrder(
        project_id=proj.id,
        user_id=user.id,
        title="Test Scope Change",
        client_request_raw="Add dark mode and animations",
        category="Minor Revision",
        risk_score=25,
        risk_level="Moderate",
        scope_delta_summary="Visual layout polish",
        analysis_json="{}",
        diplomatic_responses_json="{}",
        agreement_markdown="# ADDENDUM",
        estimated_hours=8.0,
        billable_amount=1200.0,
        currency="USD",
        status="draft"
    )
    db_session.add(co)
    db_session.commit()
    db_session.refresh(co)
    
    assert co.id is not None
    assert co.status == "draft"
    
    # Update status to approved
    co.status = "approved"
    db_session.commit()
    db_session.refresh(co)
    assert co.status == "approved"
