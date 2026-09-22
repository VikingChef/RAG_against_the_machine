import uuid

from pydantic import BaseModel, Field

class MinimalSource(BaseModel):
    """Describe where one retrieved source comes from."""

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """Represent one question before an answer has been generated."""

    question_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """Represent an answered question with its sources and generated answer."""

    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """Represent a collection of answered and unanswered RAG questions."""

    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """Represent the retrieval result for one question."""

    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Represent a search result with its generated answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """Represent evaluator-facing results for a complete search run."""

    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Represent the evaluator-facing container for a complete answer run."""

    search_results: list[MinimalAnswer]
    k: int