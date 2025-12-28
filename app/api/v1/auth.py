from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.auth import UserRegister, UserLogin, Token
from app.services.auth_service import register_user, authenticate_user

router = APIRouter()


@router.post("/register", response_model=dict)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> dict:
    user = register_user(db, email=payload.email, password=payload.password)
    return {"message": "User registered successfully", "id": user.id, "email": user.email}

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    access_token = authenticate_user(db, email=payload.email, password=payload.password)
    return Token(access_token=access_token)