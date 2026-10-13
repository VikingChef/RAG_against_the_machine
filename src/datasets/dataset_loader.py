"""Load and validate RAG dataset files."""

import json
from pathlib import Path

from pydantic import ValidationError

from src.errors.application_errors import (
    FileMissingError,
    InvalidDatasetError,
    InvalidJsonError,
)
from src.models.evaluation_models import (
    RagDataset,
    StudentSearchResults,
)


class DatasetLoader:
    """Load dataset files into validated application models."""

    def load(self, path: Path) -> RagDataset:
        """Load a question dataset and return a validated RagDataset."""
        parsed_data = self._read_json(path)

        try:
            validated_dataset = RagDataset.model_validate(parsed_data)
        except ValidationError:
            raise InvalidDatasetError(path)

        return validated_dataset

    def load_search_results(
        self,
        path: Path,
    ) -> StudentSearchResults:
        """Load and validate previously generated student search results."""
        parsed_data = self._read_json(path)

        try:
            search_results = StudentSearchResults.model_validate(
                parsed_data
            )
        except ValidationError:
            raise InvalidDatasetError(path)

        return search_results

    def _read_json(self, path: Path) -> object:
        """Read and parse JSON data from a file."""
        try:
            with path.open("r", encoding="utf-8") as file:
                parsed_data: object = json.load(file)

        except FileNotFoundError:
            raise FileMissingError(path)

        except json.JSONDecodeError:
            raise InvalidJsonError(path)

        return parsed_data
