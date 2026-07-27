from pathlib import Path
from typing import ClassVar

PROMPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "prompts"
PROMPT_SUFFIX = ".md"


class PromptRegistry:
    """Resolves a prompt name to its text.

    An agent asks for a prompt by name and never touches the filesystem, so a
    prompt can come from a markdown file, from a test, or later from a database
    without changing a single agent. Explicitly registered prompts win over the
    files, which makes overriding a prompt a one-line call.
    """

    _prompts: ClassVar[dict[str, str]] = {}

    @classmethod
    def register(cls, name: str, text: str) -> None:
        """Store a prompt under `name`, replacing anything registered before.

        Raises:
            ValueError: If the text is empty.
        """
        if not text.strip():
            raise ValueError(f"Prompt '{name}' is empty.")

        cls._prompts[cls._normalize(name)] = text

    @classmethod
    def get(cls, name: str) -> str:
        """Return the prompt registered or stored on disk under `name`.

        Raises:
            ValueError: If the name is empty.
            FileNotFoundError: If neither a registered prompt nor a file exists.
        """
        if not name.strip():
            raise ValueError(
                "No prompt name was given. An agent must declare `prompt`."
            )

        key = cls._normalize(name)
        registered = cls._prompts.get(key)

        if registered is not None:
            return registered

        return cls._load_from_disk(key)

    @classmethod
    def available(cls) -> list[str]:
        """Return every prompt name that resolves, from memory and from disk."""
        names = set(cls._prompts)

        if PROMPTS_DIRECTORY.is_dir():
            names.update(
                path.stem.lower()
                for path in PROMPTS_DIRECTORY.glob(f"*{PROMPT_SUFFIX}")
            )

        return sorted(names)

    @classmethod
    def unregister(cls, name: str) -> None:
        """Forget a prompt registered in memory. The files stay untouched."""
        cls._prompts.pop(cls._normalize(name), None)

    @classmethod
    def _load_from_disk(cls, key: str) -> str:
        path = PROMPTS_DIRECTORY / f"{key}{PROMPT_SUFFIX}"

        if not path.is_file():
            raise FileNotFoundError(
                f"Prompt '{key}' was not found. Register it with "
                f"PromptRegistry.register(), or create {path}."
            )

        text = path.read_text(encoding="utf-8")

        if not text.strip():
            raise FileNotFoundError(f"Prompt file {path} is empty.")

        return text

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().lower()
