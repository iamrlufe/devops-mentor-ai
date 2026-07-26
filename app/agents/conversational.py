import logging
from pathlib import Path
from typing import ClassVar

from app.agents.base import DEFAULT_CHAT_ID, BaseAgent
from app.memory.factory import MemoryFactory
from app.models.chat_message import ROLE_ASSISTANT, ROLE_USER, ChatMessage
from app.providers.factory import ProviderFactory
from app.rag.context_builder import ContextBuilder
from app.rag.factory import RetrieverFactory
from app.services.prompt_builder import PromptBuilder

RETRIEVAL_LIMIT = 5
PROMPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "prompts"

logger = logging.getLogger(__name__)


class ConversationalAgent(BaseAgent):
    """An agent that answers with its system prompt, the indexed documentation
    and the history of the conversation.

    Every agent of the platform shares this pipeline and differs only by its
    system prompt and its capabilities, so a new agent is a subclass with a few
    class attributes and no duplicated logic.
    """

    #: Name of the file in `app/prompts` that holds the system prompt.
    prompt_file: ClassVar[str] = ""

    def __init__(self) -> None:
        self.system_prompt = self._load_system_prompt()
        self.provider = ProviderFactory.create()
        self.memory = MemoryFactory.create()
        self.retriever = RetrieverFactory.create()

    def ask(self, prompt: str, chat_id: str = DEFAULT_CHAT_ID) -> str:
        """Answer the question and store both sides of the exchange."""
        key = self._memory_key(chat_id)

        history = [
            ChatMessage(role=item.role, content=item.content)
            for item in self.memory.load(key)
        ]
        context = self._build_context(prompt)
        messages = PromptBuilder.build(self.system_prompt, history, prompt, context)

        answer = self.provider.generate(messages)

        self.memory.save(key, ROLE_USER, prompt)
        self.memory.save(key, ROLE_ASSISTANT, answer)

        return answer

    def _build_context(self, prompt: str) -> str:
        """Look for relevant documents. A broken or missing index must not stop
        the agent from answering, so a retrieval failure only costs the
        context."""
        try:
            documents = self.retriever.search(prompt, limit=RETRIEVAL_LIMIT)
        except RuntimeError as error:
            logger.warning("Retrieval failed, answering without context: %s", error)
            return ""

        return ContextBuilder.build(documents)

    def _memory_key(self, chat_id: str) -> str:
        """Namespace the history by agent, so two agents in the same chat do not
        read each other's conversation."""
        return f"{self.name}:{chat_id}" if self.name else chat_id

    @classmethod
    def _load_system_prompt(cls) -> str:
        """Read the system prompt of the agent.

        Raises:
            FileNotFoundError: If the agent declares no prompt file, or the file
                is missing.
        """
        if not cls.prompt_file:
            raise FileNotFoundError(
                f"Agent '{cls.name or cls.__name__}' declares no prompt_file. "
                f"Add one and put the prompt into {PROMPTS_DIRECTORY}."
            )

        prompt_path = PROMPTS_DIRECTORY / cls.prompt_file

        if not prompt_path.is_file():
            raise FileNotFoundError(
                f"System prompt file was not found: {prompt_path}. "
                f"Agent '{cls.name or cls.__name__}' cannot start without it."
            )

        return prompt_path.read_text(encoding="utf-8")
