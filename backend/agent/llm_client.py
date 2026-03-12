import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI


class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("LLM_MODEL", "gpt-4")

    def generate_plan(
        self, user_message: str, context: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        messages = []

        if context:
            messages.extend(
                [{"role": msg["role"], "content": msg["content"]} for msg in context]
            )

        system_prompt = """You are an AI agent that generates execution plans.
Given a user request, output a JSON plan with this structure:
{
  "steps": [
    {"tool": "tool_name", "arguments": {"arg1": "value1"}}
  ]
}

Available tools: list_dir, read_file, write_file, search_text, run_shell_safe, get_file_info
"""

        messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        if self.client is None:
            return {"steps": []}

        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=0.7
        )

        content = response.choices[0].message.content
        if content is None:
            return {"steps": []}

        try:
            plan = json.loads(content)
            return plan
        except json.JSONDecodeError:
            return {"steps": []}
