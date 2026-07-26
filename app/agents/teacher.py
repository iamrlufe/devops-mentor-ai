import logging
from pathlib import Path

from app.memory.factory import MemoryFactory
from app.models.chat_message import ROLE_ASSISTANT, ROLE_USER, ChatMessage
from app.providers.factory import ProviderFactory
from app.rag.context_builder import ContextBuilder
from app.rag.factory import RetrieverFactory
from app.services.prompt_builder import PromptBuilder

DEFAULT_CHAT_ID = "default"
RETRIEVAL_LIMIT = 5

logger = logging.getLogger(__name__)


class TeacherAgent:

    def __init__(self):
        self.system_prompt = self._load_system_prompt()
        self.provider = ProviderFactory.create()
        self.memory = MemoryFactory.create()
        self.retriever = RetrieverFactory.create()

    def ask(self, prompt: str, chat_id: str = DEFAULT_CHAT_ID) -> str:
        history = [
            ChatMessage(role=item.role, content=item.content)
            for item in self.memory.load(chat_id)
        ]
        context = self._build_context(prompt)
        messages = PromptBuilder.build(self.system_prompt, history, prompt, context)

        answer = self.provider.generate(messages)

        self.memory.save(chat_id, ROLE_USER, prompt)
        self.memory.save(chat_id, ROLE_ASSISTANT, answer)

        return answer

    def _build_context(self, prompt: str) -> str:
        """Look for relevant documents. A broken or missing index must not stop the
        mentor from answering, so a retrieval failure only costs the context."""
        try:
            documents = self.retriever.search(prompt, limit=RETRIEVAL_LIMIT)
        except RuntimeError as error:
            logger.warning("Retrieval failed, answering without context: %s", error)
            return ""

        return ContextBuilder.build(documents)

    @staticmethod
    def _load_system_prompt() -> str:
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "teacher.md"

        if not prompt_path.is_file():
            raise FileNotFoundError(
                f"System prompt file was not found: {prompt_path}"
            )

        return prompt_path.read_text(encoding="utf-8")
