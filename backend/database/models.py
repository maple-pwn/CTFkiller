"""Database models for the LLM Agent Workspace System."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class SessionStatus(enum.Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(enum.Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ExecutionStatus(enum.Enum):
    """Execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Session(Base):
    """Session model - represents a user interaction session."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(
        SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    workspace_path = Column(String(512), nullable=True)

    # Relationships
    messages = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan"
    )
    execution_logs = relationship(
        "ExecutionLog", back_populates="session", cascade="all, delete-orphan"
    )
    policy_violations = relationship(
        "PolicyViolation", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session(session_id={self.session_id}, status={self.status.value})>"


class Message(Base):
    """Message model - represents chat messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String(255), ForeignKey("sessions.session_id"), nullable=False, index=True
    )
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role.value})>"


class ExecutionLog(Base):
    """ExecutionLog model - tracks tool execution."""

    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String(255), ForeignKey("sessions.session_id"), nullable=False, index=True
    )
    tool_name = Column(String(255), nullable=False)
    arguments = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    status = Column(
        SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False
    )
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("Session", back_populates="execution_logs")

    def __repr__(self) -> str:
        return f"<ExecutionLog(id={self.id}, tool={self.tool_name}, status={self.status.value})>"


class PolicyViolation(Base):
    """PolicyViolation model - tracks security policy violations."""

    __tablename__ = "policy_violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String(255), ForeignKey("sessions.session_id"), nullable=False, index=True
    )
    rule_name = Column(String(255), nullable=False)
    violation_details = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="policy_violations")

    def __repr__(self) -> str:
        return f"<PolicyViolation(id={self.id}, rule={self.rule_name}, severity={self.severity})>"
