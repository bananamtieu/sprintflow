from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.auth import login as api_login
from app.core.deps import get_db
from app.core.security import create_access_token, decode_token
from app.services.auth_service import authenticate_user
from app.models.user import User
from app.models.project import Project
from app.models.membership import Membership
from app.models.story import Story
from app.models.sprint import Sprint

router = APIRouter()

def get_token_from_session(request: Request) -> Optional[str]:
    return request.session.get("access_token")

def get_current_user_ui(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    payload = decode_token(token)  # should return dict with "sub"
    email = payload.get("sub")
    if not email:
        request.session.clear()
        return RedirectResponse(url="/ui/login", status_code=303)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        request.session.clear()
        return RedirectResponse(url="/ui/login", status_code=303)
    return user

@router.get("/ui/login", response_class=HTMLResponse)
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/ui/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        access_token = authenticate_user(db, email=email, password=password)
    except HTTPException:
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=400,
        )
    request.session["access_token"] = access_token
    return RedirectResponse(url="/ui/projects", status_code=303)

@router.post("/ui/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/ui/login", status_code=303)

@router.get("/ui/projects", response_class=HTMLResponse)
def projects_page(
    request: Request,
    db: Session = Depends(get_db),
    user_or_response = Depends(get_current_user_ui),
):
    if isinstance(user_or_response, RedirectResponse):
        return user_or_response
    user = user_or_response

    projects = (
        db.query(Project)
        .join(Membership, Membership.project_id == Project.id)
        .filter(Membership.user_id == user.id)
        .order_by(Project.id.desc())
        .all()
    )
    return request.app.state.templates.TemplateResponse(
        "projects.html",
        {"request": request, "user": user, "projects": projects}
    )

@router.get("/ui/projects/{project_id}", response_class=HTMLResponse)
def project_detail_page(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_or_response = Depends(get_current_user_ui),
):
    if isinstance(user_or_response, RedirectResponse):
        return user_or_response
    user = user_or_response
    
    # enforce membership
    membership = (
        db.query(Membership)
        .filter(Membership.project_id == project_id, Membership.user_id == user.id)
        .first()
    )
    if not membership:
        return RedirectResponse(url="/ui/projects", status_code=303)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    stories = db.query(Story).filter(Story.project_id == project_id).order_by(Story.id.desc()).all()
    sprints = db.query(Sprint).filter(Sprint.project_id == project_id).order_by(Sprint.id.desc()).all()

    return request.app.state.templates.TemplateResponse(
        "project_detail.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "membership": membership,
            "stories": stories,
            "sprints": sprints
        },
    )