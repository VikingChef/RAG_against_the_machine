"""Provide helper functions for indexing source files and chunks."""

import ast

from src.errors.application_errors import MissingAstPositionError


def ast_byte_converter(line: str, byte_offset: int) -> int:
    """Helper that converts AST byte offset -> character offset"""

    encoded_line = line.encode("utf-8")
    prefix_bytes = encoded_line[:byte_offset]
    prefix_text = prefix_bytes.decode("utf-8")
    return len(prefix_text)


def get_node_character_indexes(
    source_text: str,
    node: ast.stmt,
) -> tuple[int, int]:
    """Return absolute character indexes for an AST node."""
    lines = source_text.splitlines(keepends=True)
    starting_line = node.lineno - 1
    line_start_index = sum(
        len(line) for line in lines[:starting_line]
    )
    start_char_offset = ast_byte_converter(
        lines[starting_line],
        node.col_offset
    )
    first_char_index = line_start_index + start_char_offset
    if node.end_lineno is None or node.end_col_offset is None:
        raise MissingAstPositionError(type(node).__name__)
    ending_line = node.end_lineno - 1
    last_char_offset = ast_byte_converter(
        lines[ending_line],
        node.end_col_offset,
    )
    line_end_index = sum(
        len(line) for line in lines[:ending_line]
    )
    last_char_index = line_end_index + last_char_offset - 1
    return first_char_index, last_char_index
