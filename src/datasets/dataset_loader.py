"""Load and validate RAG dataset files."""

from pathlib import Path
from pydantic import ValidationError
import json

from src.models.evaluation_models import RagDataset
from src.errors.application_errors import (
    FileMissingError,
    InvalidJsonError,
    InvalidDatasetError
)


class DatasetLoader:
    """Load dataset files into validated application models."""

    def load(self, path: Path) -> RagDataset:
        """Load a dataset file and return a validated RagDataset."""

        try:
            with open(path, "r", encoding="utf-8") as file:
                parsed_data = json.load(file)

        except FileNotFoundError:
            raise FileMissingError(path)

        except json.JSONDecodeError:
            raise InvalidJsonError(path)

        try:
            validated_dataset = RagDataset.model_validate(parsed_data)

        except ValidationError:
            raise InvalidDatasetError(path)

        return validated_dataset
