"""
Test agent orchestrator with mock LLM.
"""

from datetime import datetime
from typing import Dict, List, Optional

from backend.agent.models import (
    Plan,
    Step,
    StepResult,
    ExecutionResult,
    StepStatus,
    ExecutionStatus,
    PolicyResult,
    RiskLevel,
    PolicyViolation,
    ToolExecutionError,
    MaxStepsExceeded,
    LLMError,
)
from backend.agent.planner import Planner
from backend.agent.policy_engine import PolicyEngine
from backend.agent.orchestrator import AgentOrchestrator
from backend.tools.registry import ToolRegistry
from backend.agent.tools import register_default_tools


def test_orchestrator():
    """Test the orchestrator with mock data."""

    # Create test tools
    registry = ToolRegistry()
    register_default_tools(registry)

    # Create a mock plan (skip LLM for testing)
    mock_plan = Plan(
        goal="Test reading a file",
        steps=[
            Step(
                id="step_1",
                tool="read_file",
                args={"path": "/home/pwn/sth/CTFkiller/backend/agent/orchestrator.py"},
                description="Read the orchestrator file",
            ),
            Step(
                id="step_2",
                tool="read_file",
                args={"path": "/home/pwn/sth/CTFkiller/backend/agent/planner.py"},
                description="Read the planner file",
            ),
        ],
    )

    # Create orchestrator
    orchestrator = AgentOrchestrator(
        policy_engine=PolicyEngine(), tool_registry=registry, max_steps=10
    )

    # Execute the plan
    result = orchestrator.execute_plan(mock_plan, session_id="test-session")

    print("=" * 60)
    print("ORCHESTRATOR TEST RESULTS")
    print("=" * 60)
    print(f"Session ID: {result.session_id}")
    print(f"Goal: {result.goal}")
    print(f"Status: {result.status.value}")
    print(f"Steps Executed: {result.steps_executed}/{result.steps_max}")
    print(f"Completed At: {result.completed_at}")

    if result.error_message:
        print(f"Error: {result.error_message}")

    print("\nStep Results:")
    print("-" * 60)
    for i, step_result in enumerate(result.results):
        print(f"Step {i + 1}: {step_result.step_id}")
        print(f"  Tool: {step_result.tool}")
        print(f"  Status: {step_result.status.value}")
        print(f"  Success: {step_result.success}")
        if step_result.error_message:
            print(f"  Error: {step_result.error_message}")
        if step_result.result:
            preview = (
                str(step_result.result)[:100] + "..."
                if len(str(step_result.result)) > 100
                else str(step_result.result)
            )
            print(f"  Result preview: {preview}")
        print()

    # Test max steps limit
    print("=" * 60)
    print("TESTING MAX STEPS LIMIT")
    print("=" * 60)

    long_plan = Plan(
        goal="Test max steps",
        steps=[
            Step(id=f"step_{i}", tool="list_dir", args={"path": "/"}) for i in range(15)
        ],
    )

    max_result = orchestrator.execute_plan(long_plan, session_id="max-test")
    print(f"Attempted steps: {len(long_plan.steps)}")
    print(f"Actual steps executed: {max_result.steps_executed}")
    print(f"Status: {max_result.status.value}")
    if max_result.error_message:
        print(f"Error: {max_result.error_message}")

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_orchestrator()
