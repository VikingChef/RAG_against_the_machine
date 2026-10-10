"""Count Qwen tokens and calculate remaining room for retrieved context."""

from transformers import PreTrainedTokenizerBase


class TokenBudget:
    """Track model token limits for retrieved context."""

    def __init__(
        self,
        tokenizer: PreTrainedTokenizerBase,
        total_context_tokens: int,
        reserved_generation_tokens: int,
    ) -> None:
        """Initialize the token budget with tokenizer and token limits."""

        self.tokenizer = tokenizer
        self.total_context_tokens = total_context_tokens
        self.reserved_generation_tokens = reserved_generation_tokens

    def count_tokens(
        self,
        text: str,
    ) -> int:
        """Return the number of Qwen tokens for the provided text."""

        token_ids = self.tokenizer.encode(
            text,
            add_special_tokens=False
        )

        return len(token_ids)

    def fits(
        self,
        text: str,
    ) -> bool:
        """Return whether the input fits within the model token budget."""

        input_tokens = self.count_tokens(text)

        if (
            input_tokens
            + self.reserved_generation_tokens
            > self.total_context_tokens
        ):
            return False

        return True
