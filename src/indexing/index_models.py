"""This file holds the models used internally by the indexing subsystem."""

from pathlib import Path
from pydantic import BaseModel


class LoadedSourceFile(BaseModel):
    """Represent a source file loaded from the corpus before chunking."""

    path: Path
    text: str
    file_type: str
