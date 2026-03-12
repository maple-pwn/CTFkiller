import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import OpenAI


class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("LLM_MODEL", "gpt-4")
        self.prompts_dir = Path(__file__).resolve().parent / "prompts"

    def generate_plan(
        self,
        user_message: str,
        context: Optional[List[Dict[str, str]]] = None,
        agent_type: str = "default",
    ) -> Dict[str, Any]:
        messages = []

        if context:
            messages.extend(
                [{"role": msg["role"], "content": msg["content"]} for msg in context]
            )

        system_prompt = self._build_system_prompt(agent_type)

        messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        if self.client is None:
            return {"steps": []}

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7
            )
            content = response.choices[0].message.content
        except Exception:
            return {"steps": []}

        if content is None:
            return {"steps": []}

        try:
            plan = json.loads(content)
            return plan
        except json.JSONDecodeError:
            return {"steps": []}

    def _build_system_prompt(self, agent_type: str) -> str:
        safe_agent_type = self._normalize_agent_type(agent_type)
        candidate = self.prompts_dir / f"{safe_agent_type}.txt"
        default_prompt = self.prompts_dir / "default.txt"

        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
        if default_prompt.exists():
            return default_prompt.read_text(encoding="utf-8")

        return """You are an AI agent that generates execution plans.
Given a user request, output a JSON plan with this structure:
{
  "steps": [
    {"tool": "tool_name", "arguments": {"arg1": "value1"}}
  ]
}

Available tools: list_dir, read_file, write_file, search_text, run_shell_safe, get_file_info
"""

    def _normalize_agent_type(self, agent_type: str) -> str:
        candidate = (agent_type or "default").strip().lower()
        if not re.fullmatch(r"[a-z0-9_-]+", candidate):
            return "default"
        return candidate
