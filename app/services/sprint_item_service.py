from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.sprint import Sprint
from app.models.story import Story
from app.models.sprint_item import SprintItem

def add_story_to_sprint(db: Session, *, project_id: int, sprint_id: int, story_id: int) -> SprintItem:
    # Validate Sprint existence
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id, Sprint.project_id == project_id).first()
    if not sprint:
        # You can choose 403 here too; 404 is fine for sprint planning APIs
        raise HTTPException(status_code=404, detail="Sprint not found")

    # Validate Story existence
    story = db.query(Story).filter(Story.id == story_id, Story.project_id == project_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Create SprintItem
    item = SprintItem(sprint_id=sprint_id, story_id=story_id)
    db.add(item)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Story is already in the sprint")

    db.refresh(item)
    return item

def remove_story_from_sprint(db: Session, *, project_id: int, sprint_id: int, item_id: int) -> None:
    # Ensure sprint item exists and belongs to the correct project
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id, Sprint.project_id == project_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    item = db.query(SprintItem).filter(SprintItem.id == item_id, SprintItem.sprint_id == sprint_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Sprint item not found")
    
    db.delete(item)
    db.commit()
