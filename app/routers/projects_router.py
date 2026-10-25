from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Project, ChangeOrder
from ..auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["Projects"])

class ProjectCreateRequest(BaseModel):
    project_name: str
    client_name: str
    client_email: Optional[str] = None
    baseline_sow: str
    hourly_rate: Optional[float] = None
    currency: Optional[str] = None

class ProjectUpdateRequest(BaseModel):
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    baseline_sow: Optional[str] = None
    hourly_rate: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None

@router.get("")
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.user_id == user.id).order_by(Project.created_at.desc()).all()
    
    output = []
    for p in projects:
        change_orders = db.query(ChangeOrder).filter(ChangeOrder.project_id == p.id).all()
        recovered_revenue = sum(co.billable_amount for co in change_orders if co.status in ["approved", "invoiced"])
        pending_amount = sum(co.billable_amount for co in change_orders if co.status in ["draft", "sent"])
        
        output.append({
            "id": p.id,
            "project_name": p.project_name,
            "client_name": p.client_name,
            "client_email": p.client_email,
            "baseline_sow": p.baseline_sow,
            "hourly_rate": p.hourly_rate,
            "currency": p.currency,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
            "change_orders_count": len(change_orders),
            "recovered_revenue": recovered_revenue,
            "pending_amount": pending_amount
        })
    return output

@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(req: ProjectCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.project_name.strip() or not req.baseline_sow.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project name and baseline Statement of Work (SOW) are required."
        )

    project = Project(
        user_id=user.id,
        project_name=req.project_name.strip(),
        client_name=req.client_name.strip(),
        client_email=req.client_email.strip() if req.client_email else None,
        baseline_sow=req.baseline_sow.strip(),
        hourly_rate=req.hourly_rate if req.hourly_rate is not None else user.default_hourly_rate,
        currency=req.currency if req.currency is not None else user.currency,
        status="active"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "status": "success",
        "project": {
            "id": project.id,
            "project_name": project.project_name,
            "client_name": project.client_name,
            "client_email": project.client_email,
            "baseline_sow": project.baseline_sow,
            "hourly_rate": project.hourly_rate,
            "currency": project.currency,
            "status": project.status,
            "created_at": project.created_at.isoformat()
        }
    }

@router.get("/{project_id}")
def get_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    change_orders = db.query(ChangeOrder).filter(ChangeOrder.project_id == project.id).order_by(ChangeOrder.created_at.desc()).all()

    return {
        "id": project.id,
        "project_name": project.project_name,
        "client_name": project.client_name,
        "client_email": project.client_email,
        "baseline_sow": project.baseline_sow,
        "hourly_rate": project.hourly_rate,
        "currency": project.currency,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "change_orders": [
            {
                "id": co.id,
                "title": co.title,
                "category": co.category,
                "risk_score": co.risk_score,
                "risk_level": co.risk_level,
                "billable_amount": co.billable_amount,
                "estimated_hours": co.estimated_hours,
                "status": co.status,
                "created_at": co.created_at.isoformat()
            } for co in change_orders
        ]
    }

@router.put("/{project_id}")
def update_project(project_id: int, req: ProjectUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if req.project_name is not None:
        project.project_name = req.project_name
    if req.client_name is not None:
        project.client_name = req.client_name
    if req.client_email is not None:
        project.client_email = req.client_email
    if req.baseline_sow is not None:
        project.baseline_sow = req.baseline_sow
    if req.hourly_rate is not None:
        project.hourly_rate = req.hourly_rate
    if req.currency is not None:
        project.currency = req.currency
    if req.status is not None:
        project.status = req.status

    db.commit()
    db.refresh(project)
    return {"status": "success", "message": "Project updated successfully."}

@router.delete("/{project_id}")
def delete_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    db.delete(project)
    db.commit()
    return {"status": "success", "message": "Project deleted."}
