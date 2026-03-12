from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, Enum, UUID, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Relationship

from .base import Base


class ExecutionPlan(Base):
    __tablename__ = "execution_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal = Column(Text, nullable=False)
    plan_json = Column(Text, nullable=False)
    status = Column(
        Enum(
            "pending",
            "approved",
            "rejected",
            "executing",
            "completed",
            "failed",
            name="execution_plan_status",
        ),
        nullable=False,
        default="pending",
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    completed_at = Column(TIMESTAMP(timezone=True))

    session = Relationship("Session", back_populates="execution_plans")
    tool_calls = Relationship(
        "ToolCall", back_populates="execution_plan", cascade="all, delete-orphan"
    )
