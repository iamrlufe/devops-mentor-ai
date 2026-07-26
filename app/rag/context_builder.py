from app.rag.models import Document

SEPARATOR = "-" * 32
UNKNOWN_SOURCE = "unknown"


class ContextBuilder:

    @staticmethod
    def build(documents: list[Document]) -> str:
        """Render the retrieved documents as a context block for the prompt."""
        found = [document for document in documents if document.text.strip()]

        if not found:
            return ""

        return "\n\n".join(ContextBuilder._build_block(document) for document in found)

    @staticmethod
    def _build_block(document: Document) -> str:
        metadata = document.metadata or {}

        return "\n".join(
            [
                SEPARATOR,
                "Source:",
                metadata.get("source") or UNKNOWN_SOURCE,
                "Title:",
                metadata.get("title") or document.id,
                "Text:",
                document.text.strip(),
                SEPARATOR,
            ]
        )
