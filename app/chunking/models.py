from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    document_id: str
    text: str
    order: int
    metadata: dict = field(default_factory=dict)
