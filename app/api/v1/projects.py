from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_min_role, require_project_member
from app.models.membership import Membership, MembershipRole
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.project_service import create_project

router = APIRouter()

@router.get("", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    List all projects the current user is a member of.
    """
    return db.query(Project).join(Project.memberships).filter_by(user_id=current_user.id).all()

@router.post("", response_model=ProjectOut)
def create(payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Create a new project.
    """
    project = create_project(db, key=payload.key, name=payload.name, creator_user_id=current_user.id)
    return project

@router.get("/{project_id}", response_model=ProjectOut)
def read(
    project_id: int,
    db: Session = Depends(get_db),
    _m: Membership=Depends(require_project_member),
):
    """
    Get details of a specific project by ID.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectOut)
def update(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_project_member),
):
    """
    Update a project's details.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if payload.name is not None:
        project.name = payload.name
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", response_model=dict)
def delete(
    project_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.ADMIN)),
):
    """
    Delete a project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
