from pathlib import Path

from app.memory.factory import MemoryFactory
from app.models.chat_message import ROLE_ASSISTANT, ROLE_USER, ChatMessage
from app.providers.factory import ProviderFactory
from app.services.prompt_builder import PromptBuilder

DEFAULT_CHAT_ID = "default"


class TeacherAgent:

    def __init__(self):
        self.system_prompt = self._load_system_prompt()
        self.provider = ProviderFactory.create()
        self.memory = MemoryFactory.create()

    def ask(self, prompt: str, chat_id: str = DEFAULT_CHAT_ID) -> str:
        history = [
            ChatMessage(role=item.role, content=item.content)
            for item in self.memory.load(chat_id)
        ]
        messages = PromptBuilder.build(self.system_prompt, history, prompt)

        answer = self.provider.generate(messages)

        self.memory.save(chat_id, ROLE_USER, prompt)
        self.memory.save(chat_id, ROLE_ASSISTANT, answer)

        return answer

    @staticmethod
    def _load_system_prompt() -> str:
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "teacher.md"

        if not prompt_path.is_file():
            raise FileNotFoundError(
                f"System prompt file was not found: {prompt_path}"
            )

        return prompt_path.read_text(encoding="utf-8")
