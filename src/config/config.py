"""Define application configuration values and defaults in one place."""

from dataclasses import dataclass, field


@dataclass
class Config:
    """Hold the application's configuration values and defaults."""

    model_name: str = "Qwen/Qwen3-0.6B"
    max_chunk_size: int = 2000
    default_k: int = 10
    total_context_tokens: int = 32768
    max_new_tokens: int = 2048
    text_chunk_overlap: int = 150
    allowed_extensions: list[str] = field(
        default_factory=lambda: [
            ".py", ".md", ".txt"
        ]
    )
