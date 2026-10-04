"""Provide shared retrieval utilities for BM25 tokenization."""

import re


class RetrievalTokenizer:
    """Turn text into tokens suitable for BM25 retrieval."""

    def tokenize(self, text: str) -> list[str]:
        """Take text and return normalized tokens suitable for retrieval."""

        if not text.strip():
            return []

        raw_tokens = re.findall(r"[A-Za-z0-9_]+", text)
        tokens: list[str] = []
        for raw_token in raw_tokens:
            normalized_token = raw_token.lower()
            tokens.append(normalized_token)
            identifier_components = self._split_identifier(raw_token)
            if identifier_components != [normalized_token]:
                tokens.extend(identifier_components)

        return tokens

    def _split_identifier(self, identifier: str) -> list[str]:
        """Split one identifier into useful retrieval components."""

        snake_parts = identifier.split("_")
        components: list[str] = []
        for part in snake_parts:
            camel_parts = re.findall(
                r"[A-Z]+(?=[A-Z][a-z]|\d|\b)|[A-Z]?[a-z]+|\d+",
                part,
            )
            components.extend(camel_parts)
        normalized_components = [
            component.lower()
            for component in components
        ]

        return normalized_components
