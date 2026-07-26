from pathlib import Path

PATTERN = "*.md"


class DocumentDiscovery:

    @staticmethod
    def discover(directory: Path) -> list[Path]:
        """Find every supported document under the directory, recursively."""
        if not directory.is_dir():
            raise NotADirectoryError(f"Documents directory was not found: {directory}")

        return sorted(path for path in directory.rglob(PATTERN) if path.is_file())
