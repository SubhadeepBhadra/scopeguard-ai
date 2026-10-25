import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import User, Project, ChangeOrder, TokenUsageLog, SubscriptionInvoice
from .auth import hash_password

def seed_database():
    """Seeds the database with realistic demo accounts, projects, and historical data."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        existing_user = db.query(User).filter(User.email == "director@scopeguard.ai").first()
        if existing_user:
            return

        print("Seeding ScopeGuard AI database with humanized agency data...")

        # 1. Create Director Account
        director = User(
            email="director@scopeguard.ai",
            hashed_password=hash_password("password123"),
            full_name="Subhadeep Bhadra",
            company_name="Apex Studio Labs",
            role="director",
            plan_tier="pro",
            monthly_token_quota=500000,
            monthly_tokens_used=64850,
            default_hourly_rate=150.0,
            currency="USD",
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        db.add(director)

        # 2. Create Freelancer Account
        freelancer = User(
            email="freelancer@scopeguard.ai",
            hashed_password=hash_password("password123"),
            full_name="Marcus Chen",
            company_name="Chen Product Studio",
            role="freelancer",
            plan_tier="starter",
            monthly_token_quota=100000,
            monthly_tokens_used=12400,
            default_hourly_rate=95.0,
            currency="USD",
            created_at=datetime.utcnow() - timedelta(days=45)
        )
        db.add(freelancer)
        db.commit()
        db.refresh(director)
        db.refresh(freelancer)

        # 3. Create Realistic Projects for Director
        p1 = Project(
            user_id=director.id,
            client_name="Acme Global Financial",
            client_email="contracts@acmefinancial.com",
            project_name="FinTech Dashboard & Portfolio App",
            baseline_sow=(
                "Scope of Work:\n"
                "1. Responsive 5-page financial dashboard (Overview, Accounts, Transactions, Reports, Settings).\n"
                "2. Read-only Plaid API integration for bank account balance retrieval.\n"
                "3. Standard email/password authentication with JWT.\n"
                "4. Export monthly statements to PDF/CSV.\n"
                "Exclusions: Custom payment processing, real-time trading engines, crypto wallets, and mobile native apps."
            ),
            hourly_rate=150.0,
            currency="USD",
            status="active",
            created_at=datetime.utcnow() - timedelta(days=60)
        )

        p2 = Project(
            user_id=director.id,
            client_name="Starlight Apparel Inc.",
            client_email="founders@starlightapparel.co",
            project_name="Headless E-Commerce Storefront",
            baseline_sow=(
                "Scope of Work:\n"
                "1. Custom Next.js headless storefront connecting to Shopify Storefront API.\n"
                "2. Product catalog browsing across 12 fashion categories.\n"
                "3. Slide-out cart drawer and standard Shopify checkout redirect.\n"
                "4. Brand design system implementation based on approved Figma file.\n"
                "Exclusions: Custom checkout redesign, loyalty points reward engine, multi-currency geo-routing."
            ),
            hourly_rate=150.0,
            currency="USD",
            status="active",
            created_at=datetime.utcnow() - timedelta(days=35)
        )

        p3 = Project(
            user_id=director.id,
            client_name="Nexus Care Partners",
            client_email="tech@nexuscare.org",
            project_name="HIPAA Telemedicine Booking Portal",
            baseline_sow=(
                "Scope of Work:\n"
                "1. Patient portal for scheduling appointments with certified clinicians.\n"
                "2. Two-way Google Calendar / Outlook sync for doctor availability.\n"
                "3. Secure SMS and Email appointment reminders via Twilio.\n"
                "4. HIPAA compliance data encryption in transit and rest.\n"
                "Exclusions: Live WebRTC video streaming, prescription ordering, insurance claims billing."
            ),
            hourly_rate=175.0,
            currency="USD",
            status="active",
            created_at=datetime.utcnow() - timedelta(days=20)
        )

        db.add_all([p1, p2, p3])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)
        db.refresh(p3)

        # 4. Create Historical Change Orders for Subhadeep
        co1 = ChangeOrder(
            project_id=p1.id,
            user_id=director.id,
            title="Scope Change: Stripe Multi-Currency Payment Gateway",
            client_request_raw="Hey Subhadeep! Can we quickly allow users to deposit funds directly via Stripe in USD and EUR? Should just take an afternoon right?",
            category="Scope Expansion",
            risk_score=72,
            risk_level="High",
            scope_delta_summary="Stripe/Payment gateway integration not present in original SOW deliverables.",
            analysis_json=json.dumps({
                "hours_breakdown": {"frontend": 8.0, "backend": 14.0, "design": 2.0, "qa": 6.0, "pm": 3.0, "total": 33.0},
                "detected_vectors": {"payments": True, "auth": False, "ai_features": False},
                "risk_rationale": "Payment compliance, webhook reconciliation, and ledger auditability require strict backend guards.",
                "recommendation": "Require Change Order with 50% mobilization deposit."
            }),
            diplomatic_responses_json=json.dumps({
                "accommodating": "Hi Acme Team,\n\nWe'd love to help you add Stripe multi-currency checkout! This is an out-of-scope addition totaling 33 hours ($4,950). Attached is CO-1012 for your review.",
                "firm": "Hi Acme Team,\n\nPayment gateways are explicitly listed in Section 4 exclusions of our SOW. We have prepared Change Order #1012 ($4,950) to authorize this addition.",
                "executive": "Hi Acme Team,\n\nAdding multi-currency payment processing now adds $4,950 and +6 days to the release date. Let us know if you want to prioritize this over the PDF statement generator.",
                "tradeoff": "Hi Acme Team,\n\nWe can either swap the custom statement exporter for this gateway, or approve CO-1012 as an additional deliverable."
            }),
            agreement_markdown="# CHANGE ORDER ADDENDUM CO-1012\n\n**Project:** FinTech Dashboard & Portfolio App\n**Total Value:** $4,950.00 USD\n**Schedule Impact:** +6 Business Days",
            estimated_hours=33.0,
            billable_amount=4950.0,
            delivery_days_impact=6,
            currency="USD",
            status="approved",
            tokens_used=1840,
            ai_cost_usd=0.00184,
            created_at=datetime.utcnow() - timedelta(days=28),
            approved_at=datetime.utcnow() - timedelta(days=26)
        )

        co2 = ChangeOrder(
            project_id=p2.id,
            user_id=director.id,
            title="Scope Change: Dynamic Tiered Loyalty Points Engine",
            client_request_raw="We want VIP shoppers to accumulate points and get instant discounts at cart. Also need tier badges.",
            category="Scope Expansion",
            risk_score=58,
            risk_level="High",
            scope_delta_summary="Loyalty rewards and dynamic discount engine exceed Shopify storefront catalog scope.",
            analysis_json=json.dumps({
                "hours_breakdown": {"frontend": 10.0, "backend": 12.0, "design": 4.0, "qa": 4.0, "pm": 2.0, "total": 32.0},
                "detected_vectors": {"payments": False, "auth": True, "ai_features": False},
                "risk_rationale": "Requires customer metadata persistence and cart discount calculations.",
                "recommendation": "Execute standard addendum."
            }),
            diplomatic_responses_json=json.dumps({
                "accommodating": "Hi Starlight Team,\n\nA loyalty rewards program will drive retention! Our engineering estimation is 32 hours ($4,800). Attached is CO-1015.",
                "firm": "Hi Starlight Team,\n\nPer our SOW Section 3, loyalty programs are an add-on. Attached is Change Order CO-1015.",
                "executive": "Hi Starlight Team,\n\nInvesting $4,800 in a loyalty engine will increase LTV. Review the attached addendum to approve.",
                "tradeoff": "Hi Starlight Team,\n\nWe can swap the 3 bonus landing pages for this loyalty feature, or add it for $4,800."
            }),
            agreement_markdown="# CHANGE ORDER ADDENDUM CO-1015\n\n**Project:** Headless E-Commerce Storefront\n**Total Value:** $4,800.00 USD\n**Schedule Impact:** +6 Business Days",
            estimated_hours=32.0,
            billable_amount=4800.0,
            delivery_days_impact=6,
            currency="USD",
            status="invoiced",
            tokens_used=1620,
            ai_cost_usd=0.00162,
            created_at=datetime.utcnow() - timedelta(days=15),
            approved_at=datetime.utcnow() - timedelta(days=14)
        )

        co3 = ChangeOrder(
            project_id=p3.id,
            user_id=director.id,
            title="Scope Change: WebRTC Encrypted Video Calling Room",
            client_request_raw="Our doctors want to conduct the consultation right inside the web page via video instead of using Zoom links.",
            category="Architectural Pivot",
            risk_score=88,
            risk_level="Critical",
            scope_delta_summary="Real-time WebRTC media servers and signaling infrastructure exceed standard booking portal.",
            analysis_json=json.dumps({
                "hours_breakdown": {"frontend": 16.0, "backend": 24.0, "design": 6.0, "qa": 12.0, "pm": 6.0, "total": 64.0},
                "detected_vectors": {"payments": False, "auth": True, "ai_features": False},
                "risk_rationale": "High bandwidth media streaming, TURN/STUN server management, and HIPAA compliance risks.",
                "recommendation": "Major Phase 2 architectural addendum recommended."
            }),
            diplomatic_responses_json=json.dumps({
                "accommodating": "Hi Nexus Team,\n\nIn-app video is a game-changer! Because of HIPAA video streaming compliance, this requires 64 engineering hours ($11,200).",
                "firm": "Hi Nexus Team,\n\nSection 5 specifically excludes WebRTC. We have outlined Addendum CO-1019 for your executive sign-off.",
                "executive": "Hi Nexus Team,\n\nDeploying custom video adds 12 days to launch and $11,200. We recommend launching on schedule with secure Zoom links first.",
                "tradeoff": "Hi Nexus Team,\n\nWe can postpone the SMS notifications and doctor reporting to fund part of the video room build."
            }),
            agreement_markdown="# CHANGE ORDER ADDENDUM CO-1019\n\n**Project:** HIPAA Telemedicine Booking Portal\n**Total Value:** $11,200.00 USD\n**Schedule Impact:** +12 Business Days",
            estimated_hours=64.0,
            billable_amount=11200.0,
            delivery_days_impact=12,
            currency="USD",
            status="sent",
            tokens_used=2450,
            ai_cost_usd=0.00245,
            created_at=datetime.utcnow() - timedelta(days=3),
            approved_at=None
        )

        db.add_all([co1, co2, co3])
        db.commit()

        # 5. Token Usage Logs
        logs = [
            TokenUsageLog(
                user_id=director.id,
                change_order_id=co1.id,
                model_used="scopeguard-neural-v2",
                prompt_tokens=420,
                completion_tokens=1420,
                total_tokens=1840,
                cost_usd=0.00184,
                operation="scope_analysis",
                created_at=datetime.utcnow() - timedelta(days=28)
            ),
            TokenUsageLog(
                user_id=director.id,
                change_order_id=co2.id,
                model_used="scopeguard-neural-v2",
                prompt_tokens=380,
                completion_tokens=1240,
                total_tokens=1620,
                cost_usd=0.00162,
                operation="scope_analysis",
                created_at=datetime.utcnow() - timedelta(days=15)
            ),
            TokenUsageLog(
                user_id=director.id,
                change_order_id=co3.id,
                model_used="scopeguard-neural-v2",
                prompt_tokens=520,
                completion_tokens=1930,
                total_tokens=2450,
                cost_usd=0.00245,
                operation="scope_analysis",
                created_at=datetime.utcnow() - timedelta(days=3)
            )
        ]
        db.add_all(logs)

        # 6. Subscription Invoices
        invoices = [
            SubscriptionInvoice(
                user_id=director.id,
                invoice_number="INV-2026-0081",
                plan_tier="pro",
                amount=79.0,
                currency="USD",
                status="paid",
                payment_method="Mastercard ending in 4242",
                created_at=datetime.utcnow() - timedelta(days=60)
            ),
            SubscriptionInvoice(
                user_id=director.id,
                invoice_number="INV-2026-0149",
                plan_tier="pro",
                amount=79.0,
                currency="USD",
                status="paid",
                payment_method="Mastercard ending in 4242",
                created_at=datetime.utcnow() - timedelta(days=30)
            )
        ]
        db.add_all(invoices)

        db.commit()
        print("Database successfully seeded with realistic agency data!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
