import logging

from app.agents.base import DEFAULT_CHAT_ID, BaseAgent
from app.models.chat_message import ROLE_ASSISTANT, ROLE_USER, ChatMessage
from app.rag.context_builder import ContextBuilder
from app.runtime.context import RuntimeContext, RuntimeContextBuilder
from app.services.prompt_builder import PromptBuilder

RETRIEVAL_LIMIT = 5

logger = logging.getLogger(__name__)


class ConversationalAgent(BaseAgent):
    """An agent that answers with its system prompt, the indexed documentation
    and the history of the conversation.

    Every agent of the platform shares this pipeline and differs only by the
    class attributes it declares, so a new agent is a subclass with no
    duplicated logic. The agent creates nothing: it receives a `RuntimeContext`
    with the prompt, the provider, the memory and the retriever already
    resolved, which is what lets a workspace run it on another stack.
    """

    def __init__(self, context: RuntimeContext | None = None) -> None:
        """Bind the agent to a runtime context.

        Args:
            context: The resolved stack to run on. Without one the agent builds
                the context from what it declares, which keeps `Agent()` working
                exactly as before workspaces existed.
        """
        self.context = context or RuntimeContextBuilder.build(type(self))
        self.system_prompt = self.context.prompt
        self.provider = self.context.provider
        self.memory = self.context.memory
        self.retriever = self.context.retriever

    def ask(self, prompt: str, chat_id: str = DEFAULT_CHAT_ID) -> str:
        """Answer the question and store both sides of the exchange."""
        key = self.memory_key(chat_id)

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

    def memory_key(self, chat_id: str) -> str:
        """Return the key this agent stores the history of a chat under.

        The history is namespaced by agent, so two agents in the same chat do
        not read each other's conversation.
        """
        return f"{self.name}:{chat_id}" if self.name else chat_id
