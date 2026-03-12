"""
Agent module for the Policy-Constrained LLM Agent.

This module provides the core agent orchestration functionality:
- Plan generation using LLM
- Policy validation
- Step execution
- Execution orchestration

Components:
    - Planner: Generates execution plans from user requests
    - PolicyEngine: Validates steps against security policies
    - Orchestrator: Coordinates plan execution
    - ToolRegistry: Manages available tools
"""

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

__all__ = [
    # Models
    "Plan",
    "Step",
    "StepResult",
    "ExecutionResult",
    "StepStatus",
    "ExecutionStatus",
    "PolicyResult",
    "RiskLevel",
    # Exceptions
    "PolicyViolation",
    "ToolExecutionError",
    "MaxStepsExceeded",
    "LLMError",
    # Agents
    "Planner",
    "PolicyEngine",
    "AgentOrchestrator",
    # Tools
    "ToolRegistry",
]

__version__ = "0.1.0"
