"""Manage model loading, caching, and Qwen-specific formatting."""

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)


class ModelManager:
    """Manage lazy model resources and model-specific prompt formatting."""

    def __init__(
        self,
        model_name: str,
    ) -> None:
        """Initialize the manager with unloaded model resources."""

        self.model_name = model_name
        self._tokenizer: PreTrainedTokenizerBase | None = None
        self._model: PreTrainedModel | None = None

    @property
    def tokenizer(
        self,
    ) -> PreTrainedTokenizerBase:
        """Return the tokenizer, loading and caching it if needed."""

        if self._tokenizer is None:
            self._tokenizer = (
                AutoTokenizer.from_pretrained(self.model_name)
            )

        if not isinstance(self._tokenizer, PreTrainedTokenizerBase):
            raise TypeError(
                "Loaded tokenizer is not a valid pretrained tokenizer"
            )

        return self._tokenizer

    @property
    def model(
        self,
    ) -> PreTrainedModel:
        """Return the model, loading and caching it if needed."""

        if self._model is None:
            self._model = (
                AutoModelForCausalLM.from_pretrained(self.model_name)
            )

        if not isinstance(self._model, PreTrainedModel):
            raise TypeError("Loaded model is not a valid pretrained model")

        return self._model

    def format_prompt(
        self,
        prompt: str,
    ) -> str:
        """Apply the model chat template to a semantic prompt."""

        messages: list[dict[str, str]] = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        if not isinstance(formatted_prompt, str):
            raise TypeError(
                "Formatted prompt is not a string"
            )

        return formatted_prompt
