from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, Enum, UUID, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Relationship

from .base import Base


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("execution_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_id = Column(String(255), nullable=False)
    tool_name = Column(String(255), nullable=False)
    arguments = Column(Text, nullable=False)
    result = Column(Text)
    status = Column(
        Enum("pending", "running", "success", "failed", name="tool_call_status"),
        nullable=False,
        default="pending",
    )
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    error_message = Column(Text)

    execution_plan = Relationship("ExecutionPlan", back_populates="tool_calls")
