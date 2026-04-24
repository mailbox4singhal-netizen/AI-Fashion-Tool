"""Auth routes — SRS §4.1."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_token, hash_password, verify_password, get_current_user
from app.database import get_db
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_dto(u: User) -> dict:
    return {"id": u.id, "name": u.name, "email": u.email, "role": u.role}


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role if payload.role in {"designer", "shopper", "admin"} else "designer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, {"role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": _user_dto(user)}


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    token = create_token(user.id, {"role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": _user_dto(user)}


# OAuth2 form-style for Swagger "Authorize" button
@router.post("/token", response_model=TokenResponse)
def token_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_token(user.id, {"role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": _user_dto(user)}


@router.get("/me")
def me(current: User = Depends(get_current_user)):
    return _user_dto(current)
