"""Finds and loads eligible source files from a corpus."""

from pathlib import Path

from src.indexing.index_models import LoadedSourceFile
from src.errors.application_errors import (
    InvalidCorpusRootError,
    SourceFileReadError
)


class CorpusLoader:
    """Loads eligible files from a corpus into LoadedSourceFile objects"""

    def __init__(self, allowed_extensions: list[str]) -> None:
        self.allowed_extensions = allowed_extensions

    def load(self, corpus_root: Path) -> list[LoadedSourceFile]:
        """Load eligible source files from the corpus."""

        if not corpus_root.exists() or not corpus_root.is_dir():
            raise InvalidCorpusRootError(corpus_root)

        loaded_files = []

        for path in corpus_root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in self.allowed_extensions:
                continue

            try:
                file_text = path.read_text(encoding="utf-8")

            except (OSError, UnicodeDecodeError):
                raise SourceFileReadError(path)

            source = LoadedSourceFile(
                path=path,
                text=file_text,
                file_type=path.suffix,
            )
            loaded_files.append(source)

        return loaded_files
