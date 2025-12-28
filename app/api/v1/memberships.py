from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_min_role, require_project_member
from app.models.membership import Membership, MembershipRole
from app.schemas.membership import MembershipInvite, MembershipOut, MembershipUpdate
from app.services.membership_service import add_member_by_email, remove_member, update_member_role

router = APIRouter()

@router.get("", response_model=List[MembershipOut])
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_project_member),
):
    """List all members of a project."""
    memberships = db.query(Membership).filter(Membership.project_id == project_id).all()
    return memberships

@router.post("", response_model=MembershipOut, status_code=status.HTTP_201_CREATED)
def invite_member(
    project_id: int,
    payload: MembershipInvite,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.ADMIN)),
):
    """Invite a new member to the project by email."""
    membership = add_member_by_email(db, project_id=project_id, user_email=str(payload.user_email), role=payload.role)
    return membership

@router.patch("/{membership_id}", response_model=MembershipOut)
def change_role(
    project_id: int,
    membership_id: int,
    payload: MembershipUpdate,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.ADMIN)),
):
    """Change the role of an existing project member."""
    membership = update_member_role(db, project_id=project_id, membership_id=membership_id, role=payload.role)
    return membership

@router.delete("/{membership_id}", response_model=dict)
def delete_member(
    project_id: int,
    membership_id: int,
    db: Session = Depends(get_db),
    current_membership: Membership = Depends(require_min_role(MembershipRole.ADMIN)),
):
    """Remove a member from the project."""

    # Optional guard: prevent removing yourself (common safety)
    if current_membership.id == membership_id:
        raise HTTPException(status_code=400, detail="Admins cannot remove themselves")
    remove_member(db, project_id=project_id, membership_id=membership_id)
    return {"message": "Member removed successfully"}