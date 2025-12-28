from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_project_member, require_min_role
from app.models.membership import Membership, MembershipRole
from app.models.sprint import Sprint
from app.schemas.sprint import SprintCreate, SprintOut, SprintUpdate
from app.services.sprint_service import create_sprint, start_sprint, close_sprint

router = APIRouter()

def _get_sprint_or_404(db: Session, project_id: int, sprint_id: int) -> Sprint:
    sprint = db.query(Sprint).filter(
        Sprint.id == sprint_id,
        Sprint.project_id == project_id
    ).first()
    if not sprint:
        # you can also choose 403 for anti-enumeration; keeping 404 for sprint here is OK
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    return sprint

@router.get("/projects/{project_id}/sprints", response_model=List[SprintOut])
def list_sprints(
    project_id: int,
    db: Session = Depends(get_db),
    _m = Depends(require_project_member),  # viewer+
):
    return db.query(Sprint).filter(Sprint.project_id == project_id).order_by(Sprint.id.desc()).all()

@router.post("/projects/{project_id}/sprints", response_model=SprintOut, status_code=status.HTTP_201_CREATED)
def create_project_sprint(
    project_id: int,
    payload: SprintCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _m: Membership = Depends(require_min_role(MembershipRole.MEMBER)),
):
    return create_sprint(
        db,
        project_id=project_id,
        creator_user_id=user.id,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

@router.get("/projects/{project_id}/sprints/{sprint_id}", response_model=SprintOut)
def read_sprint(
    project_id: int,
    sprint_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_project_member),
):
    return _get_sprint_or_404(db, project_id, sprint_id)

@router.patch("/projects/{project_id}/sprints/{sprint_id}", response_model=SprintOut)
def patch_sprint(
    project_id: int,
    sprint_id: int,
    payload: SprintUpdate,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.MEMBER)),
):
    sprint = _get_sprint_or_404(db, project_id, sprint_id)

    if payload.name is not None:
        sprint.name = payload.name
    if payload.start_date is not None:
        sprint.start_date = payload.start_date
    if payload.end_date is not None:
        sprint.end_date = payload.end_date
    if payload.status is not None:
        sprint.status = payload.status
    
    db.commit()
    db.refresh(sprint)
    return sprint

@router.post("/projects/{project_id}/sprints/{sprint_id}/start", response_model=SprintOut)
def start(
    project_id: int,
    sprint_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.MEMBER)),
):
    sprint = _get_sprint_or_404(db, project_id, sprint_id)
    return start_sprint(db, sprint=sprint)

@router.post("/projects/{project_id}/sprints/{sprint_id}/close", response_model=SprintOut)
def close(
    project_id: int,
    sprint_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.MEMBER)),
):
    sprint = _get_sprint_or_404(db, project_id, sprint_id)
    return close_sprint(db, sprint=sprint)

@router.delete("/projects/{project_id}/sprints/{sprint_id}", response_model=dict)
def delete(
    project_id: int,
    sprint_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.ADMIN)),
):
    sprint = _get_sprint_or_404(db, project_id, sprint_id)
    db.delete(sprint)
    db.commit()
    return {"message": "Sprint deleted"}
