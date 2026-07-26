from app.agents.teacher import DEFAULT_CHAT_ID, TeacherAgent
from app.models.chat_message import ROLE_ASSISTANT, ROLE_USER, ChatMessage
from app.providers.base import BaseProvider
from app.providers.factory import ProviderFactory
from app.providers.gemini import GeminiProvider
from app.rag.base import Retriever
from app.rag.empty import EmptyRetriever
from app.rag.factory import RetrieverFactory
from app.rag.models import Document

QUESTION = "How do I build a Docker image?"
PREVIEW_LENGTH = 320

HISTORY = [
    (ROLE_USER, "What is a container?"),
    (ROLE_ASSISTANT, "A running instance of an image."),
]

DOCUMENTS = [
    Document(
        id="Docker-0001",
        text="Docker builds an image from a Dockerfile with `docker build -t app .`",
        metadata={
            "title": "Docker",
            "source": "docs/demo/Docker.md",
            "text": "Docker builds an image from a Dockerfile with `docker build -t app .`",
        },
        score=0.7040,
    ),
    Document(
        id="Git-0001",
        text="Git stores the project history as a chain of commits.",
        metadata={
            "title": "Git",
            "source": "docs/demo/Git.md",
            "text": "Git stores the project history as a chain of commits.",
        },
        score=0.5636,
    ),
]


class MockProvider(BaseProvider):
    """Records the messages instead of calling Gemini."""

    def __init__(self):
        self.messages: list[ChatMessage] = []

    def generate(self, messages: list[ChatMessage]) -> str:
        self.messages = messages
        return "Mock answer."


class StubRetriever(Retriever):
    """Returns prepared documents, or fails the way a missing index does."""

    def __init__(self, documents=(), error: Exception | None = None):
        self.documents = list(documents)
        self.error = error

    def search(self, query: str, limit: int = 5) -> list[Document]:
        if self.error:
            raise self.error

        return self.documents[:limit]


def preview(text: str) -> str:
    single_line = " ".join(text.split())

    if len(single_line) <= PREVIEW_LENGTH:
        return single_line

    return f"{single_line[:PREVIEW_LENGTH]}... ({len(text)} chars)"


def show(title: str, retriever: Retriever) -> None:
    mock = MockProvider()
    ProviderFactory.create = staticmethod(lambda: mock)
    RetrieverFactory._retriever = retriever

    agent = TeacherAgent()
    agent.memory.clear(DEFAULT_CHAT_ID)

    for role, text in HISTORY:
        agent.memory.save(DEFAULT_CHAT_ID, role, text)

    answer = agent.ask(QUESTION)

    print(f"\n{'=' * 70}")
    print(title)
    print("=" * 70)
    print(f"Answer: {answer}")
    print(f"Messages sent to the provider: {len(mock.messages)}\n")

    for number, message in enumerate(mock.messages, start=1):
        print(f"  {number}. [{message.role}] {preview(message.content)}")

    system_instruction, contents = GeminiProvider._to_gemini_format(mock.messages)
    print("\n  Gemini sees:")
    print(f"    system_instruction: {preview(system_instruction)}")
    print(f"    contents: {[content.role for content in contents]}")

    agent.memory.clear(DEFAULT_CHAT_ID)


show("WITHOUT RAG (nothing found)", EmptyRetriever())
show("WITH RAG (two documents found)", StubRetriever(DOCUMENTS))
show(
    "RETRIEVER FAILS (missing collection) - the mentor still answers",
    StubRetriever(error=RuntimeError("Collection 'mentor_documents' does not exist.")),
)
