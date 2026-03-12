from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, BigInteger, UUID, TIMESTAMP
from sqlalchemy.orm import Relationship

from .base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    plan_template = Column(Text, nullable=False)
    parameters = Column(Text, nullable=False)
    created_by = Column(String(255), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    usage_count = Column(BigInteger, nullable=False, default=0)
