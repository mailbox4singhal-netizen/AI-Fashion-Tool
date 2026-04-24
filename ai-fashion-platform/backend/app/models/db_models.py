"""SQLAlchemy ORM models matching the SRS schema (§3.1 – 3.5)."""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="designer")  # designer | shopper | admin
    created_at = Column(DateTime, default=datetime.utcnow)

    requests = relationship("Request", back_populates="user")


class Request(Base):
    __tablename__ = "requests"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    input_type = Column(String)
    input_data = Column(JSON)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="requests")
    results = relationship("AIResult", back_populates="request", cascade="all, delete-orphan")


class AIResult(Base):
    __tablename__ = "ai_results"

    id = Column(String, primary_key=True, default=_uuid)
    request_id = Column(String, ForeignKey("requests.id"))
    module = Column(String)  # trend | color | design | techpack
    output = Column(JSON)
    confidence = Column(Float)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("Request", back_populates="results")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=_uuid)
    request_id = Column(String, ForeignKey("requests.id"))
    model_version = Column(String)
    prompt_version = Column(String)
    input = Column(JSON)
    output = Column(JSON)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Config(Base):
    __tablename__ = "config"

    key = Column(String, primary_key=True)
    value = Column(String)
