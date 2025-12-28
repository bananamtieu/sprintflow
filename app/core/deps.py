from __future__ import annotations

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User
from app.models.membership import Membership, MembershipRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

ROLE_RANK = {
    MembershipRole.ADMIN: 3,
    MembershipRole.MEMBER: 2,
    MembershipRole.VIEWER: 1,
}

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        if not subject:
            raise ValueError("Missing subject in token")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = db.query(User).filter(User.email == subject).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def require_project_member(
    project_id: int = Path(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    membership = (
        db.query(Membership)
        .filter(Membership.project_id == project_id, Membership.user_id == user.id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of the project",
        )
    return membership

def require_min_role(min_role: MembershipRole):
    def _dep(
        project_id: int = Path(...),
        membership: Membership = Depends(require_project_member),
    ) -> Membership:
        if ROLE_RANK[membership.role] < ROLE_RANK[min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the required role: {min_role}",
            )
        return membership
    return _dep

def assert_project_member(
    db: Session,
    *,
    user_id: int,
    project_id: int
) -> Membership:
    membership = (
        db.query(Membership)
        .filter(Membership.project_id == project_id, Membership.user_id == user_id)
        .first()
    )
    if not membership:
        # anti-enumeration policy
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this project",
        )
    return membership

def assert_min_role(
    db: Session,
    *,
    user_id: int,
    project_id: int,
    min_role: MembershipRole,
) -> Membership:
    membership = assert_project_member(db, user_id=user_id, project_id=project_id)
    if ROLE_RANK[membership.role] < ROLE_RANK[min_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have the required role: {min_role}",
        )
    return membership