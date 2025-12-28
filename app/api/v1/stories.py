from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_min_role, require_project_member, assert_project_member, assert_min_role
from app.models.membership import Membership, MembershipRole
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryOut, StoryUpdate
from app.services.story_service import create_story, update_story

router = APIRouter()


# -------- Project-scoped endpoints --------
@router.get("/projects/{project_id}/stories", response_model=List[StoryOut])
def list_project_stories(
    project_id: int,
    db: Session = Depends(get_db),
    _m: Membership = Depends(require_project_member),  # viewer+ can read
):
    return db.query(Story).filter(Story.project_id == project_id).order_by(Story.id.desc()).all()

@router.post("/projects/{project_id}/stories", response_model=StoryOut, status_code=status.HTTP_201_CREATED)
def create_project_story(
    project_id: int,
    payload: StoryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _m: Membership = Depends(require_min_role(MembershipRole.MEMBER)),
):
    return create_story(
        db,
        project_id=project_id,
        creator_user_id=user.id,
        title=payload.title,
        description=payload.description,
        type=payload.story_type,
        priority=payload.priority,
        story_points=payload.story_points,
        assignee_id=payload.assignee_id,
    )


# -------- Story-id endpoints --------
def get_story_or_404(db: Session, story_id: int) -> Story:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    return story

@router.get("/stories/{story_id}", response_model=StoryOut)
def read_story(
    story_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    story = get_story_or_404(db, story_id)
    assert_project_member(db, user_id=user.id, project_id=story.project_id)
    return story

@router.patch("/stories/{story_id}", response_model=StoryOut)
def patch_story(
    story_id: int,
    payload: StoryUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    story = get_story_or_404(db, story_id)
    assert_min_role(db, user_id=user.id, project_id=story.project_id, min_role=MembershipRole.MEMBER)
    return update_story(db, story=story, payload=payload)

@router.delete("/stories/{story_id}", response_model=dict)
def delete_story(
    story_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    story = get_story_or_404(db, story_id)
    assert_min_role(db, user_id=user.id, project_id=story.project_id, min_role=MembershipRole.ADMIN)

    db.delete(story)
    db.commit()
    return {"message": "Story deleted successfully"}