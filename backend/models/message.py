from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, Enum, UUID, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Relationship

from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(
        Enum("user", "assistant", "system", name="message_role"), nullable=False
    )
    content = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    session = Relationship("Session", back_populates="messages")
