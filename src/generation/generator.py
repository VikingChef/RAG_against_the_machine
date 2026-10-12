"""Generate answer text from model-formatted prompts."""

from typing import Any, cast

from src.generation.model_manager import ModelManager


class Generator:
    """Generate answer text from a formatted model prompt."""

    def __init__(
        self,
        model_manager: ModelManager,
        max_new_tokens: int,
    ) -> None:
        """Initialize the generator with shared model resources."""

        self.model_manager = model_manager
        self.max_new_tokens = max_new_tokens

    def generate(
        self,
        formatted_prompt: str,
    ) -> str:
        """Generate answer text from a formatted model prompt."""

        model_inputs = self.model_manager.tokenizer(
            formatted_prompt,
            return_tensors="pt",
        )

        model = cast(Any, self.model_manager.model)

        generated_tokens = model.generate(
            **model_inputs,
            max_new_tokens=self.max_new_tokens,
        )

        input_length = model_inputs["input_ids"].shape[1]
        answer_tokens = generated_tokens[0][input_length:]

        answer_text = self.model_manager.tokenizer.decode(
            answer_tokens,
            skip_special_tokens=True,
        )

        if not isinstance(answer_text, str):
            raise TypeError(
                "Answer text is not a string"
            )

        return answer_text
