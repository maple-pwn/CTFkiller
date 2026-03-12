"""
LLM-based Planner for generating execution plans.
"""

import json
import os
from typing import Dict, List, Optional

from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from backend.agent.models import Plan, Step, LLMError


class Planner:
    """Generates execution plans using LLM with structured output."""

    MAX_RETRIES = 3
    RETRY_WAIT_MIN = 1  # seconds
    RETRY_WAIT_MAX = 30  # seconds

    PLAN_SYSTEM_PROMPT = """You are an expert task planner for a security-constrained environment.
Your task is to break down a user's request into a sequence of tool calls that can be executed
in a sandboxed environment.

CRITICAL REQUIREMENTS:
1. Only use tools from the allowed list
2. Each step must have exactly one tool call
3. Arguments must be valid JSON-serializable objects
4. Prioritize safety - use read_file before write_file when unsure
5. Keep steps atomic and focused on single tasks
6. No forbidden operations (rm -rf, sudo, chmod, etc.)

Return your response as a JSON object with:
- goal: Restated user goal in clear terms
- steps: Array of step objects, each with:
  - tool: Name of the tool to use
  - args: Dictionary of arguments for the tool
  - description: Brief description of what this step does
"""

    ALLOWED_TOOLS = [
        "list_dir",
        "read_file",
        "write_file",
        "search_text",
        "run_python",
        "run_shell_safe",
        "extract_archive",
        "get_file_info",
    ]

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the planner.

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
            model: Model to use for plan generation.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not provided and not found in environment")

        self.model = model
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_plan(self, user_message: str, context: Optional[Dict] = None) -> Plan:
        """
        Generate an execution plan from a user message.

        Args:
            user_message: User's request
            context: Optional context (e.g., previous steps, session info)

        Returns:
            Plan object with goal and steps

        Raises:
            LLMError: If plan generation fails after retries
        """
        prompt = self._build_prompt(user_message, context)

        try:
            response = self._call_llm_with_retry(prompt)
            return self._parse_response(response)
        except Exception as e:
            raise LLMError(f"Failed to generate plan: {str(e)}")

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),
        retry=retry_if_exception_type((LLMError, Exception)),
        reraise=True,
    )
    def _call_llm_with_retry(self, prompt: str) -> str:
        """
        Call LLM with retry logic.

        Args:
            prompt: Prompt to send to LLM

        Returns:
            Raw response text from LLM

        Raises:
            LLMError: If all retries fail
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.PLAN_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                timeout=60,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMError(f"LLM API call failed: {str(e)}")

    def _build_prompt(self, user_message: str, context: Optional[Dict]) -> str:
        """Build the prompt for LLM."""
        prompt_parts = []

        prompt_parts.append(f"USER REQUEST:\n{user_message}\n")

        if context:
            prompt_parts.append("\nCONTEXT:\n")
            prompt_parts.append(f"Session ID: {context.get('session_id', 'N/A')}")
            if "allowed_tools" in context:
                prompt_parts.append(f"Allowed tools: {context['allowed_tools']}")
            if "max_steps" in context:
                prompt_parts.append(f"Max steps: {context['max_steps']}")

        prompt_parts.append(f"\nallowed_tools: {self.ALLOWED_TOOLS}")
        prompt_parts.append("\nReturn ONLY valid JSON response.")

        return "\n".join(prompt_parts)

    def _parse_response(self, response: str) -> Plan:
        """Parse LLM response into Plan object."""
        try:
            data = json.loads(response)

            if not isinstance(data, dict):
                raise LLMError("Response is not a JSON object")

            if "goal" not in data:
                raise LLMError("Response missing 'goal' field")

            if "steps" not in data:
                raise LLMError("Response missing 'steps' field")

            if not isinstance(data["steps"], list):
                raise LLMError("'steps' must be a list")

            steps = []
            for i, step_data in enumerate(data["steps"]):
                if not isinstance(step_data, dict):
                    raise LLMError(f"Step {i} is not a JSON object")

                if "tool" not in step_data:
                    raise LLMError(f"Step {i} missing 'tool' field")

                if "args" not in step_data:
                    raise LLMError(f"Step {i} missing 'args' field")

                step = Step(
                    id=f"step_{i}",
                    tool=step_data["tool"],
                    args=step_data["args"],
                    description=step_data.get(
                        "description", f"Execute {step_data['tool']}"
                    ),
                )
                steps.append(step)

            return Plan(goal=data["goal"], steps=steps)

        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise LLMError(f"Error parsing response: {str(e)}")
