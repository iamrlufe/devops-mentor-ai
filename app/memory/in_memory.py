import threading

from app.config import settings
from app.memory.base import MemoryProvider
from app.memory.models import Message
from app.memory.registry import MemoryRegistry


@MemoryRegistry.register("in_memory")
class InMemoryMemoryProvider(MemoryProvider):
    """Demo provider: keeps the history in the process memory.

    It is lost on restart. `PostgresMemoryProvider` is what a running
    deployment uses.

    The history of a chat is capped by `MEMORY_MAX_MESSAGES`: nothing evicts it
    otherwise, so a long lived chat would grow without bound and take the prompt
    with it. The newest messages are kept.
    """

    def __init__(self) -> None:
        self._history: dict[str, list[Message]] = {}
        self._lock = threading.Lock()

    def load(self, chat_id: str) -> list[Message]:
        with self._lock:
            return list(self._history.get(chat_id, []))

    def save(self, chat_id: str, role: str, text: str) -> None:
        with self._lock:
            history = self._history.setdefault(chat_id, [])
            history.append(Message(role=role, content=text))

            limit = settings.memory_max_messages

            if limit > 0 and len(history) > limit:
                del history[:-limit]

    def clear(self, chat_id: str) -> None:
        with self._lock:
            self._history.pop(chat_id, None)
