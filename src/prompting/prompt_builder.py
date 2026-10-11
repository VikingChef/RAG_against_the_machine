"""Build the semantic prompt from a Query and a ContextResult."""

from src.models.query import Query
from src.models.context_result import ContextResult


class PromptBuilder:
    """Build the model-facing prompt from a query and formatted context."""

    def build(
        self,
        query: Query,
        context: ContextResult,
    ) -> str:
        """Takes Query + ContextResult and returns a semantic prompt string."""

        prompt = (
            "Answer the question using only the provided context.\n"
            "If the context does not contain enough information, say so.\n\n"
            f"Question:\n{query.text}\n\n"
            f"Context:\n{context.context_text}\n\n"
            "Answer:"
        )

        return prompt
