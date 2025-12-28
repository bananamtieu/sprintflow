from pydantic import BaseModel

class SprintItemCreate(BaseModel):
    story_id: int

class SprintItemOut(BaseModel):
    id: int
    sprint_id: int
    story_id: int

    model_config = {"from_attributes": True}