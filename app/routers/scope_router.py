import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Project, ChangeOrder, TokenUsageLog
from ..auth import get_current_user
from ..ai_engine import scope_engine

router = APIRouter(prefix="/api/scope", tags=["Scope Analysis"])

class AnalyzeScopeRequest(BaseModel):
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    baseline_sow: Optional[str] = None
    client_request_raw: str
    hourly_rate: Optional[float] = None
    currency: Optional[str] = None

class StatusUpdateRequest(BaseModel):
    status: str  # 'draft', 'sent', 'approved', 'rejected', 'invoiced'

@router.post("/analyze")
def analyze_scope(
    req: AnalyzeScopeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.client_request_raw.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client request text is required."
        )

    # Quota check
    if user.monthly_tokens_used >= user.monthly_token_quota:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Monthly AI token quota exceeded for your plan. Please upgrade your subscription."
        )

    # Resolve project details
    project = None
    if req.project_id:
        project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == user.id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        project_name = project.project_name
        client_name = project.client_name
        baseline_sow = project.baseline_sow
        hourly_rate = req.hourly_rate or project.hourly_rate or user.default_hourly_rate
        currency = req.currency or project.currency or user.currency
    else:
        project_name = req.project_name or "Custom Client Project"
        client_name = req.client_name or "Client"
        baseline_sow = req.baseline_sow or "Standard MVP web application deliverables."
        hourly_rate = req.hourly_rate or user.default_hourly_rate
        currency = req.currency or user.currency

        # Automatically create or associate a project if none provided
        project = Project(
            user_id=user.id,
            project_name=project_name,
            client_name=client_name,
            baseline_sow=baseline_sow,
            hourly_rate=hourly_rate,
            currency=currency,
            status="active"
        )
        db.add(project)
        db.commit()
        db.refresh(project)

    # User BYOK configuration
    user_keys = {}
    if user.custom_groq_key:
        user_keys["groq_key"] = user.custom_groq_key
    if user.custom_openai_key:
        user_keys["openai_key"] = user.custom_openai_key

    # Run AI Analysis
    analysis_res, prompt_tokens, comp_tokens, cost_usd, model_used = scope_engine.analyze(
        project_name=project_name,
        client_name=client_name,
        baseline_sow=baseline_sow,
        client_request=req.client_request_raw,
        hourly_rate=hourly_rate,
        currency=currency,
        user_keys=user_keys
    )

    total_tokens = prompt_tokens + comp_tokens

    # Persist Change Order
    change_order = ChangeOrder(
        project_id=project.id,
        user_id=user.id,
        title=analysis_res["title"],
        client_request_raw=req.client_request_raw.strip(),
        category=analysis_res["category"],
        risk_score=analysis_res["risk_score"],
        risk_level=analysis_res["risk_level"],
        scope_delta_summary=analysis_res["scope_delta_summary"],
        analysis_json=json.dumps(analysis_res["analysis_details"]),
        diplomatic_responses_json=json.dumps(analysis_res["diplomatic_responses"]),
        agreement_markdown=analysis_res["agreement_markdown"],
        estimated_hours=analysis_res["estimated_hours"],
        billable_amount=analysis_res["billable_amount"],
        delivery_days_impact=analysis_res["delivery_days_impact"],
        currency=currency,
        status="draft",
        tokens_used=total_tokens,
        ai_cost_usd=cost_usd,
        created_at=datetime.utcnow()
    )
    db.add(change_order)

    # FinOps Token Accounting Log
    token_log = TokenUsageLog(
        user_id=user.id,
        change_order_id=None,
        model_used=model_used,
        prompt_tokens=prompt_tokens,
        completion_tokens=comp_tokens,
        total_tokens=total_tokens,
        cost_usd=cost_usd,
        operation="scope_analysis"
    )
    db.add(token_log)

    # Update User token consumption
    user.monthly_tokens_used += total_tokens

    db.commit()
    db.refresh(change_order)
    token_log.change_order_id = change_order.id
    db.commit()

    return {
        "status": "success",
        "change_order_id": change_order.id,
        "project_id": project.id,
        "analysis": {
            "title": change_order.title,
            "category": change_order.category,
            "risk_score": change_order.risk_score,
            "risk_level": change_order.risk_level,
            "scope_delta_summary": change_order.scope_delta_summary,
            "estimated_hours": change_order.estimated_hours,
            "billable_amount": change_order.billable_amount,
            "delivery_days_impact": change_order.delivery_days_impact,
            "currency": change_order.currency,
            "analysis_details": analysis_res["analysis_details"],
            "diplomatic_responses": analysis_res["diplomatic_responses"],
            "agreement_markdown": change_order.agreement_markdown,
            "status": change_order.status
        },
        "finops": {
            "model_used": model_used,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": comp_tokens,
            "total_tokens": total_tokens,
            "ai_cost_usd": cost_usd,
            "monthly_tokens_used": user.monthly_tokens_used,
            "monthly_token_quota": user.monthly_token_quota
        }
    }

@router.get("/change-orders")
def list_change_orders(
    project_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(ChangeOrder).filter(ChangeOrder.user_id == user.id)
    if project_id:
        q = q.filter(ChangeOrder.project_id == project_id)
    if status_filter:
        q = q.filter(ChangeOrder.status == status_filter)

    cos = q.order_by(ChangeOrder.created_at.desc()).all()

    output = []
    for co in cos:
        project = db.query(Project).filter(Project.id == co.project_id).first()
        output.append({
            "id": co.id,
            "project_id": co.project_id,
            "project_name": project.project_name if project else "Unknown",
            "client_name": project.client_name if project else "Unknown",
            "title": co.title,
            "category": co.category,
            "risk_score": co.risk_score,
            "risk_level": co.risk_level,
            "billable_amount": co.billable_amount,
            "estimated_hours": co.estimated_hours,
            "delivery_days_impact": co.delivery_days_impact,
            "currency": co.currency,
            "status": co.status,
            "tokens_used": co.tokens_used,
            "ai_cost_usd": co.ai_cost_usd,
            "created_at": co.created_at.isoformat(),
            "approved_at": co.approved_at.isoformat() if co.approved_at else None
        })
    return output

@router.get("/change-orders/{co_id}")
def get_change_order(co_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    co = db.query(ChangeOrder).filter(ChangeOrder.id == co_id, ChangeOrder.user_id == user.id).first()
    if not co:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change order not found.")

    project = db.query(Project).filter(Project.id == co.project_id).first()

    return {
        "id": co.id,
        "project_id": co.project_id,
        "project_name": project.project_name if project else "Unknown",
        "client_name": project.client_name if project else "Unknown",
        "baseline_sow": project.baseline_sow if project else "",
        "title": co.title,
        "client_request_raw": co.client_request_raw,
        "category": co.category,
        "risk_score": co.risk_score,
        "risk_level": co.risk_level,
        "scope_delta_summary": co.scope_delta_summary,
        "estimated_hours": co.estimated_hours,
        "billable_amount": co.billable_amount,
        "delivery_days_impact": co.delivery_days_impact,
        "currency": co.currency,
        "status": co.status,
        "analysis_details": json.loads(co.analysis_json) if co.analysis_json else {},
        "diplomatic_responses": json.loads(co.diplomatic_responses_json) if co.diplomatic_responses_json else {},
        "agreement_markdown": co.agreement_markdown,
        "tokens_used": co.tokens_used,
        "ai_cost_usd": co.ai_cost_usd,
        "created_at": co.created_at.isoformat(),
        "approved_at": co.approved_at.isoformat() if co.approved_at else None
    }

@router.patch("/change-orders/{co_id}/status")
def update_change_order_status(
    co_id: int,
    req: StatusUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    co = db.query(ChangeOrder).filter(ChangeOrder.id == co_id, ChangeOrder.user_id == user.id).first()
    if not co:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change order not found.")

    valid_statuses = ["draft", "sent", "approved", "rejected", "invoiced"]
    if req.status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Status must be one of {valid_statuses}")

    co.status = req.status
    if req.status == "approved" and not co.approved_at:
        co.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(co)

    return {"status": "success", "message": f"Change order marked as {req.status}."}

@router.get("/change-orders/{co_id}/export")
def export_change_order_markdown(co_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    co = db.query(ChangeOrder).filter(ChangeOrder.id == co_id, ChangeOrder.user_id == user.id).first()
    if not co:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change order not found.")

    return Response(
        content=co.agreement_markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=Change_Order_{co.id}.md"}
    )
