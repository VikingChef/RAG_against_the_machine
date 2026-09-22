from pydantic import BaseModel, Field, field_validator


class Query(BaseModel):
    """Represent a single search or answer request."""

    text: str
    k: int = Field(ge=0)


    @field_validator("text")
    def validate_text(cls, value) -> str:
        if value.strip() == "":
            raise ValueError(
                "Query must not be empty"
            )
        return value
