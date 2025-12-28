from pydantic import BaseModel, Field
from typing import Optional

class ProjectCreate(BaseModel):
    key: str = Field(min_length=2, max_length=16, pattern=r'^[A-Z][A-Z0-9_]*$')
    name: str = Field(min_length=1, max_length=120)

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)

class ProjectOut(BaseModel):
    id: int
    key: str
    name: str

    model_config = {"from_attributes": True}
