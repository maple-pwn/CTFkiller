from typing import Dict, Any, List
from datetime import datetime
from backend.agent.llm_client import LLMClient
from backend.policy.engine import PolicyEngine
from backend.tools.gateway import ToolGateway
from backend.database.models import (
    Session,
    Message,
    ExecutionLog,
    MessageRole,
    ExecutionStatus,
)
from backend.database.connection import get_db


class AgentOrchestrator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.policy_engine = PolicyEngine()
        self.tool_gateway = ToolGateway()

    def process_request(
        self, session_id: str, user_message: str, agent_type: str = "default"
    ) -> Dict[str, Any]:
        db = next(get_db())
        try:
            db.add(
                Message(
                    session_id=session_id, role=MessageRole.USER, content=user_message
                )
            )
            db.commit()

            messages = (
                db.query(Message)
                .filter(Message.session_id == session_id)
                .order_by(Message.created_at)
                .all()
            )
            context = [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages[-10:]
            ]

            plan = self.llm_client.generate_plan(user_message, context, agent_type)

            valid, violations = self.policy_engine.validate_execution_plan(
                plan, session_id
            )
            if not valid:
                response = f"Policy violation: {', '.join(violations)}"
                db.add(
                    Message(
                        session_id=session_id,
                        role=MessageRole.ASSISTANT,
                        content=response,
                    )
                )
                db.commit()
                return {
                    "success": False,
                    "response": response,
                    "violations": violations,
                }

            results = []
            for step in plan.get("steps", []):
                log = ExecutionLog(
                    session_id=session_id,
                    tool_name=step["tool"],
                    arguments=str(step.get("arguments", {})),
                    status=ExecutionStatus.RUNNING,
                    started_at=datetime.utcnow(),
                )
                db.add(log)
                db.commit()

                tool_result = self.tool_gateway.execute_tool(
                    session_id, step["tool"], step.get("arguments", {})
                )

                log.status = (
                    ExecutionStatus.COMPLETED
                    if tool_result["success"]
                    else ExecutionStatus.FAILED
                )
                log.result = str(tool_result.get("result", ""))
                log.error = tool_result.get("error", "")
                log.completed_at = datetime.utcnow()
                db.commit()

                results.append(tool_result)

            response = self._format_response(results)
            db.add(
                Message(
                    session_id=session_id, role=MessageRole.ASSISTANT, content=response
                )
            )
            db.commit()

            return {"success": True, "response": response, "results": results}
        finally:
            db.close()

    def _format_response(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "No actions were executed."

        successful = sum(1 for r in results if r.get("success"))
        total = len(results)

        response = f"Executed {successful}/{total} actions successfully.\n\n"
        for i, result in enumerate(results, 1):
            if result.get("success"):
                response += f"{i}. ✓ Success\n"
            else:
                response += f"{i}. ✗ Failed: {result.get('error', 'Unknown error')}\n"

        return response
