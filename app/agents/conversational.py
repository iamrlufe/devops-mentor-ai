import logging

from app.agents.base import DEFAULT_CHAT_ID, BaseAgent
from app.memory.factory import MemoryFactory
from app.models.chat_message import ROLE_ASSISTANT, ROLE_USER, ChatMessage
from app.prompting.registry import PromptRegistry
from app.providers.factory import ProviderFactory
from app.rag.context_builder import ContextBuilder
from app.rag.factory import RetrieverFactory
from app.services.prompt_builder import PromptBuilder

RETRIEVAL_LIMIT = 5

logger = logging.getLogger(__name__)


class ConversationalAgent(BaseAgent):
    """An agent that answers with its system prompt, the indexed documentation
    and the history of the conversation.

    Every agent of the platform shares this pipeline and differs only by the
    class attributes it declares, so a new agent is a subclass with no
    duplicated logic. The pipeline resolves the prompt through the
    `PromptRegistry` and the rest of the stack through factories, which is why
    an agent can run on another model, memory or collection without any change
    here.
    """

    def __init__(self) -> None:
        self.system_prompt = PromptRegistry.get(self.prompt)
        self.provider = ProviderFactory.create(self.default_provider)
        self.memory = MemoryFactory.create(self.default_memory)
        self.retriever = RetrieverFactory.create(
            self.default_retriever,
            self.collection,
        )

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
