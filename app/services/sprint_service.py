from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sprint import Sprint, SprintStatus


def create_sprint(db: Session, *, project_id: int, creator_user_id: int, name: str, start_date=None, end_date=None) -> Sprint:
    new_sprint = Sprint(
        project_id=project_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        created_by=creator_user_id,
        status=SprintStatus.PLANNED,
    )
    db.add(new_sprint)
    db.commit()
    db.refresh(new_sprint)
    return new_sprint

def start_sprint(db: Session, *, sprint: Sprint) -> Sprint:
    # Optional Scrum rule: only one ACTIVE per project
    active = db.query(Sprint).filter(
        Sprint.project_id == sprint.project_id,
        Sprint.status == SprintStatus.ACTIVE,
    ).first()
    if active and active.id != sprint.id:
        raise HTTPException(status_code=400, detail="Another sprint is already ACTIVE")
    
    sprint.status = SprintStatus.ACTIVE
    db.commit()
    db.refresh(sprint)
    return sprint

def close_sprint(db: Session, *, sprint: Sprint) -> Sprint:
    sprint.status = SprintStatus.CLOSED
    db.commit()
    db.refresh(sprint)
    return sprint