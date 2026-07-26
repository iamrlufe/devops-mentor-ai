from pathlib import Path

from app.providers.factory import ProviderFactory


class TeacherAgent:

    def __init__(self):
        self.system_prompt = self._load_system_prompt()
        self.provider = ProviderFactory.create()

    def ask(self, prompt: str) -> str:
        return self.provider.generate(f"{self.system_prompt}\n\n{prompt}")

    @staticmethod
    def _load_system_prompt() -> str:
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "teacher.md"

        if not prompt_path.is_file():
            raise FileNotFoundError(
                f"System prompt file was not found: {prompt_path}"
            )

        return prompt_path.read_text(encoding="utf-8")
