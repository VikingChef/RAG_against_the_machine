"""Define application-specific exceptions for the RAG system."""

from pathlib import Path


class FileMissingError(Exception):
    """Raised when file is missing"""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"No file present at {path}")


class InvalidJsonError(Exception):
    """Raised when json syntax is broken"""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Invalid JSON syntax in {path}")


class InvalidDatasetError(Exception):
    """Raised when RAG dataset structure is mismatching"""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Invalid RAG dataset structure in {path}")


class DatasetWriteError(Exception):
    """Raised when dataset output cannot be written."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Could not write the dataset output to {path}")


class InvalidCorpusRootError(Exception):
    """Raised when the corpus root is invalid"""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Invalid corpus root: {path}")


class SourceFileReadError(Exception):
    """Raised when an eligible source file cannot be read."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Could not read source file: {path}")


class MissingAstPositionError(Exception):
    """Raised when an AST node lacks end_lineno or end_col_offset."""

    def __init__(self, node_type: str) -> None:
        self.node_type = node_type
        super().__init__(f"Missing AST position for node type: {node_type}")
