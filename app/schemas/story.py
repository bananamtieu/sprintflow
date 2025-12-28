from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from app.models.story import Priority, StoryStatus, StoryType
from typing import Optional

FIB_POINTS = {0, 1, 2, 3, 5, 8, 13, 21}

class StoryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    story_type: StoryType = StoryType.STORY
    priority: Priority = Priority.P2
    story_points: Optional[int] = Field(None, description="Story points must be a Fibonacci number", ge=0)
    assignee_id: Optional[int] = None

    def model_post_init(self, __context) -> None:
        if self.story_points is not None and self.story_points not in FIB_POINTS:
            raise ValueError(f"story_points must be one of the Fibonacci numbers: {FIB_POINTS}")

class StoryUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    story_type: Optional[StoryType] = None
    priority: Optional[Priority] = None
    story_points: Optional[int] = Field(None, description="Story points must be a Fibonacci number", ge=0)
    status: Optional[StoryStatus] = None
    assignee_id: Optional[int] = None

    def model_post_init(self, __context) -> None:
        if self.story_points is not None and self.story_points not in FIB_POINTS:
            raise ValueError(f"story_points must be one of the Fibonacci numbers: {FIB_POINTS}")

class StoryOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    story_type: StoryType
    priority: Priority
    story_points: Optional[int]
    status: StoryStatus
    assignee_id: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class StoryTransition(BaseModel):
    to_status: StoryStatus
