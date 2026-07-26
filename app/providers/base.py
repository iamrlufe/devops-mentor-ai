from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from LLM."""
        raise NotImplementedError