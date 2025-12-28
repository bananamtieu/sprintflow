from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.membership import MembershipRole
from app.models.story import Story
from app.models.user import User

def create_story(db: Session, *, project_id: int, creator_user_id: int, title: str, description: Optional[str], type, priority, story_points: Optional[int], assignee_id: Optional[int]) -> Story:
    # Optional: validate assignee exists
    if assignee_id:
        assignee = db.query(User).filter(User.id == assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
    
    new_story = Story(
        project_id=project_id,
        title=title,
        description=description,
        story_type=type,
        priority=priority,
        story_points=story_points,
        assignee_id=assignee_id,
        created_by=creator_user_id,
    )
    db.add(new_story)
    db.commit()
    db.refresh(new_story)
    return new_story

def update_story(db: Session, *, story: Story, payload) -> Story:
    # payload is StoryUpdate
    for field in ('title', 'description', 'story_type', 'priority', 'story_points', 'status', 'assignee_id'):
        value = getattr(payload, field)
        if value is not None:
            setattr(story, field, value)
    
    db.commit()
    db.refresh(story)
    return story