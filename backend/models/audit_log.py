from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, Enum, UUID, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Relationship

from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL")
    )
    user_id = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    session = Relationship("Session", back_populates="audit_logs")
