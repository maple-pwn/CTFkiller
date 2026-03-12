from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, BigInteger, UUID, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Relationship

from .base import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path = Column(String(1024), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(255), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    session = Relationship("Session", back_populates="artifacts")
