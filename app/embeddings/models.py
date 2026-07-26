from dataclasses import dataclass, field


@dataclass
class Embedding:
    chunk_id: str
    vector: list[float]
    metadata: dict = field(default_factory=dict)
