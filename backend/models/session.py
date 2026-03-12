from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Relationship

from .base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    status = Column(
        Enum("active", "completed", "failed", name="session_status"),
        nullable=False,
        default="active",
    )
    workspace_path = Column(String(1024), nullable=False)

    messages = Relationship(
        "Message", back_populates="session", cascade="all, delete-orphan"
    )
    execution_plans = Relationship(
        "ExecutionPlan", back_populates="session", cascade="all, delete-orphan"
    )
    artifacts = Relationship(
        "Artifact", back_populates="session", cascade="all, delete-orphan"
    )
    audit_logs = Relationship("AuditLog", back_populates="session")
