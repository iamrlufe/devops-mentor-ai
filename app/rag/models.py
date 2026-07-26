from dataclasses import dataclass, field


@dataclass
class Document:
    id: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)
    score: float = 0.0
