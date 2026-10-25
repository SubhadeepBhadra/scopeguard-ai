from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255), default="Digital Studio")
    role = Column(String(50), default="director")  # 'director', 'freelancer', 'pm'
    
    # Subscription & FinOps Quotas
    plan_tier = Column(String(50), default="pro")  # 'starter', 'pro', 'agency'
    billing_cycle = Column(String(20), default="monthly")
    monthly_token_quota = Column(Integer, default=500000)
    monthly_tokens_used = Column(Integer, default=0)
    
    # Billing defaults
    default_hourly_rate = Column(Float, default=125.0)
    currency = Column(String(10), default="USD")
    
    # Custom API Key integration (optional BYOK)
    custom_groq_key = Column(String(255), nullable=True)
    custom_openai_key = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    change_orders = relationship("ChangeOrder", back_populates="user", cascade="all, delete-orphan")
    token_logs = relationship("TokenUsageLog", back_populates="user", cascade="all, delete-orphan")
    invoices = relationship("SubscriptionInvoice", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=True)
    project_name = Column(String(255), nullable=False)
    baseline_sow = Column(Text, nullable=False)
    hourly_rate = Column(Float, default=125.0)
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="active")  # 'active', 'completed', 'archived'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="projects")
    change_orders = relationship("ChangeOrder", back_populates="project", cascade="all, delete-orphan")

class ChangeOrder(Base):
    __tablename__ = "change_orders"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    client_request_raw = Column(Text, nullable=False)
    
    # AI Analysis Results
    category = Column(String(100), default="Scope Expansion")  # 'Minor Revision', 'Scope Expansion', 'Architectural Pivot'
    risk_score = Column(Integer, default=50)  # 1 - 100
    risk_level = Column(String(50), default="Moderate")  # 'Low', 'Moderate', 'High', 'Critical'
    scope_delta_summary = Column(Text, nullable=False)
    analysis_json = Column(Text, nullable=False)  # JSON-encoded details
    diplomatic_responses_json = Column(Text, nullable=False)  # JSON-encoded 4 tones
    agreement_markdown = Column(Text, nullable=False)  # Formatted legal addendum
    
    # Financials & Timing
    estimated_hours = Column(Float, default=10.0)
    billable_amount = Column(Float, default=1250.0)
    delivery_days_impact = Column(Integer, default=5)
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="draft")  # 'draft', 'sent', 'approved', 'rejected', 'invoiced'
    
    # FinOps Token Accounting
    tokens_used = Column(Integer, default=0)
    ai_cost_usd = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="change_orders")
    user = relationship("User", back_populates="change_orders")

class TokenUsageLog(Base):
    __tablename__ = "token_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_order_id = Column(Integer, nullable=True)
    model_used = Column(String(100), default="gemini-1.5-pro")
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    operation = Column(String(100), default="scope_analysis")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="token_logs")

class SubscriptionInvoice(Base):
    __tablename__ = "subscription_invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_number = Column(String(100), unique=True, nullable=False)
    plan_tier = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="paid")  # 'paid', 'pending', 'refunded'
    payment_method = Column(String(100), default="Visa ending in 4242")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")
