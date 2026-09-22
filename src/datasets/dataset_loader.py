"""Load and validate RAG dataset files."""

import json

from src.models.evaluation_models import RagDataset


class DatasetLoader:
    """Load dataset files into validated application models."""

    def load(self, path: str) -> RagDataset:
        """Load a dataset file and return a validated RagDataset."""

        with open(path, "r", encoding="utf-8") as file:
            parsed_data = json.load(file)
            validated_dataset = RagDataset.model_validate(parsed_data)
            return validated_dataset
