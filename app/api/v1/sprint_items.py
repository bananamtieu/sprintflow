from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_min_role, require_project_member
from app.models.membership import Membership, MembershipRole
from app.models.sprint import Sprint
from app.models.sprint_item import SprintItem
from app.schemas.sprint_item import SprintItemCreate, SprintItemOut
from app.services.sprint_item_service import add_story_to_sprint, remove_story_from_sprint

router = APIRouter()


def _get_sprint_or_404(db: Session, project_id: int, sprint_id: int) -> SprintItem:
    sprint = db.query(Sprint).filter(
        Sprint.id == sprint_id,
        Sprint.project_id == project_id
    ).first()
    if not sprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found.")
    return sprint


@router.get("/projects/{project_id}/sprints/{sprint_id}/items", response_model=List[SprintItemOut])
def list_items(
    project_id: int,
    sprint_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_project_member),  # viewer+
):
    _get_sprint_or_404(db, project_id, sprint_id)
    return db.query(SprintItem).filter(SprintItem.sprint_id==sprint_id).order_by(SprintItem.id.asc()).all()

@router.post("/projects/{project_id}/sprints/{sprint_id}/items", response_model=SprintItemOut, status_code=status.HTTP_201_CREATED)
def add_item(
    project_id: int,
    sprint_id: int,
    payload: SprintItemCreate,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.MEMBER)),  # member+
):
    _get_sprint_or_404(db, project_id, sprint_id)
    return add_story_to_sprint(db, project_id=project_id, sprint_id=sprint_id, story_id=payload.story_id)

@router.delete("/projects/{project_id}/sprints/{sprint_id}/items/{item_id}", response_model=dict)
def delete_item(
    project_id: int,
    sprint_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_min_role(MembershipRole.MEMBER)),  # member+
):
    _get_sprint_or_404(db, project_id, sprint_id)
    remove_story_from_sprint(db, project_id=project_id, sprint_id=sprint_id, item_id=item_id)
    return {"message": "Sprint item removed successfully."}