from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.sprint import SprintStatus

class SprintCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    '''
    @model_validator(mode='after')
    def check_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return self
    '''

class SprintUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[SprintStatus] = None  # allow direct status changes if you want

    '''
    @model_validator(mode='after')
    def check_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return self
    '''

class SprintOut(BaseModel):
    id: int
    project_id: int
    name: str
    status: SprintStatus
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class SprintItemCreate(BaseModel):
    story_id: int
