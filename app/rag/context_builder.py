HEADER = "Relevant documentation:"
SEPARATOR = "-" * 16


class ContextBuilder:

    @staticmethod
    def build(documents: list[str]) -> str:
        """Render the retrieved documents as a context block for the prompt."""
        found = [document.strip() for document in documents if document.strip()]

        if not found:
            return ""

        parts = [HEADER]
        for document in found:
            parts.append(SEPARATOR)
            parts.append(document)

        return "\n\n".join(parts)
