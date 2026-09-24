"""Responsible for writing validated dataset result to Json Files"""

import json
from pathlib import Path

from src.models.evaluation_models import (
    StudentSearchResults,
    StudentSearchResultsAndAnswer
)
from src.errors.application_errors import DatasetWriteError


class DataSetWriter:
    """Write validated dataset results to JSON files."""

    def write(
        self,
        data: StudentSearchResults | StudentSearchResultsAndAnswer,
        path: Path,
    ) -> None:

        output_data = data.model_dump()

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(output_data, file, indent=4)

        except OSError:
            raise DatasetWriteError(path)
