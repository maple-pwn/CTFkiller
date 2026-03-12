from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from backend.database.connection import get_db
from backend.database.models import (
    Session,
    Message,
    ExecutionLog,
    SessionStatus,
    MessageRole,
)
from backend.agent.orchestrator import AgentOrchestrator
from backend.workspace.fs import WorkspaceManager

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
orchestrator = AgentOrchestrator()
workspace_manager = WorkspaceManager()


class CreateSessionRequest(BaseModel):
    pass


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: datetime


class SendMessageRequest(BaseModel):
    content: str
    agent_type: Optional[str] = "default"


class SendMessageResponse(BaseModel):
    success: bool
    response: str
    violations: Optional[List[str]] = None


@router.post("", response_model=CreateSessionResponse)
def create_session(db: DBSession = Depends(get_db)):
    session_id = str(uuid.uuid4())
    workspace_manager.create_session_workspace(session_id)

    session = Session(session_id=session_id, status=SessionStatus.ACTIVE)
    db.add(session)
    db.commit()
    db.refresh(session)

    return CreateSessionResponse(
        session_id=session.session_id,
        status=session.status.value,
        created_at=session.created_at,
    )


@router.post("/{session_id}/messages", response_model=SendMessageResponse)
def send_message(
    session_id: str, request: SendMessageRequest, db: DBSession = Depends(get_db)
):
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = orchestrator.process_request(
        session_id, request.content, request.agent_type or "default"
    )

    return SendMessageResponse(
        success=result["success"],
        response=result["response"],
        violations=result.get("violations"),
    )


@router.get("/{session_id}/messages")
def get_messages(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )

    return [
        {
            "id": msg.id,
            "role": msg.role.value,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        }
        for msg in messages
    ]


@router.get("/{session_id}/logs")
def get_execution_logs(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.session_id == session_id)
        .order_by(ExecutionLog.started_at)
        .all()
    )

    return [
        {
            "id": log.id,
            "tool_name": log.tool_name,
            "arguments": log.arguments,
            "result": log.result,
            "status": log.status.value,
            "error": log.error,
            "started_at": log.started_at.isoformat(),
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        }
        for log in logs
    ]
