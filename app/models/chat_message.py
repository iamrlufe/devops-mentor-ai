from dataclasses import dataclass

ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    role: str
    content: str
