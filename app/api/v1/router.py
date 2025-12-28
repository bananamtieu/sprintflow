from fastapi import APIRouter
from app.api.v1 import auth, projects, memberships, stories, sprints, sprint_items

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(memberships.router, prefix="/projects/{project_id}/memberships", tags=["memberships"])
api_router.include_router(stories.router, tags=["stories"])
api_router.include_router(sprints.router, tags=["sprints"])
api_router.include_router(sprint_items.router, tags=["sprint_items"])