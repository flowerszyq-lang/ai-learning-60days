import json
from pathlib import Path

PROMPTS_FILE = Path(__file__).parent.parent / "config" / "prompts.json"

class PromptManager:
    def __init__(self):
        self.prompts = self._load_prompts()

    def _load_prompts(self):
        if PROMPTS_FILE.exists():
            with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_system_prompt(self, role: str = "default") -> str:
        return self.prompts.get(role, self.prompts.get("default", "你是银行客服专家。"))

    def reload(self):
        self.prompts = self._load_prompts()