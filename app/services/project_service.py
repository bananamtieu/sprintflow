from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.membership import Membership, MembershipRole

def create_project(db: Session, *, key: str, name: str, creator_user_id: int) -> Project:
    existing_project = db.query(Project).filter(Project.key == key).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="Project with this key already exists.")
    
    new_project = Project(key=key, name=name, created_by=creator_user_id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    creator_membership = Membership(
        user_id=creator_user_id,
        project_id=new_project.id,
        role=MembershipRole.ADMIN
    )
    db.add(creator_membership)
    db.commit()
    return new_project