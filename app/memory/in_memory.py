from app.memory.base import MemoryProvider
from app.memory.models import Message
from app.memory.registry import MemoryRegistry


@MemoryRegistry.register("in_memory")
class InMemoryMemoryProvider(MemoryProvider):
    """Keeps the history in the process memory. It is lost on restart."""

    def __init__(self) -> None:
        self._history: dict[str, list[Message]] = {}

    def load(self, chat_id: str) -> list[Message]:
        return list(self._history.get(chat_id, []))

    def save(self, chat_id: str, role: str, text: str) -> None:
        self._history.setdefault(chat_id, []).append(Message(role=role, content=text))

    def clear(self, chat_id: str) -> None:
        self._history.pop(chat_id, None)
