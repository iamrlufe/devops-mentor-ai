from app.config import settings
from app.database.repositories.memory_repository import MemoryRepository
from app.memory.base import MemoryProvider
from app.memory.models import Message
from app.memory.registry import MemoryRegistry


@MemoryRegistry.register("postgres")
class PostgresMemoryProvider(MemoryProvider):
    """Keeps the prompt window in PostgreSQL, so a restart keeps the thread.

    Memory stays a short window: `MEMORY_MAX_MESSAGES` still bounds it, and the
    conversation tables hold the full history, so trimming here loses nothing.
    """

    def load(self, chat_id: str) -> list[Message]:
        rows = MemoryRepository.load(chat_id, settings.memory_max_messages)

        return [Message(role=row["role"], content=row["content"]) for row in rows]

    def save(self, chat_id: str, role: str, text: str) -> None:
        MemoryRepository.save(chat_id, role, text, settings.memory_max_messages)

    def clear(self, chat_id: str) -> None:
        MemoryRepository.clear(chat_id)
