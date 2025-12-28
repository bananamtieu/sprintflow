from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.membership import Membership, MembershipRole
from app.models.user import User

def add_member_by_email(db: Session, *, project_id: int, user_email: str, role: MembershipRole) -> Membership:
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_membership = Membership(
        user_id=user.id,
        project_id=project_id,
        role=role
    )
    db.add(new_membership)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # likely UniqueConstraint(user_id, project_id)
        raise HTTPException(status_code=400, detail="User is already a member of this project")
    
    db.refresh(new_membership)
    return new_membership

def update_member_role(db: Session, *, project_id: int, membership_id: int, role: MembershipRole) -> Membership:
    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.project_id == project_id
    ).first()
    if not membership:
        # keeping it simple: return 404 for membership itself
        raise HTTPException(status_code=404, detail="Membership not found")

    membership.role = role
    db.commit()
    db.refresh(membership)
    return membership

def remove_member(db: Session, *, project_id: int, membership_id: int) -> None:
    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.project_id == project_id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    db.delete(membership)
    db.commit()
