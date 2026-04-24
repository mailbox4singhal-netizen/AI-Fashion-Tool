"""JWT + bcrypt auth utilities + role-based access control."""
from datetime import datetime, timedelta
from typing import Iterable, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# Canonical role set. Keep in sync with frontend Login role selector.
VALID_ROLES = {"designer", "shopper", "admin"}


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(subject: str, extra: Optional[dict] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def require_role(*allowed: str):
    """Dependency factory returning a dependency that only allows users
    whose `.role` is in `allowed`.

    Usage:
        @router.post(..., dependencies=[Depends(require_role("admin"))])
        # or
        def handler(user: User = Depends(require_role("designer", "admin"))): ...
    """
    allowed_set = set(allowed)

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_set:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Requires one of roles: {sorted(allowed_set)}. You are '{user.role}'.",
            )
        return user

    return dependency


# Convenience shortcuts
def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin role required")
    return user


def require_designer_or_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"designer", "admin"}:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Designers and admins can create or modify designs; shoppers cannot.",
        )
    return user
