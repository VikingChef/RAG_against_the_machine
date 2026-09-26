"""Use Python's AST to split source code into structured chunks."""

import ast

from src.indexing.index_models import LoadedSourceFile
from src.indexing.indexing_utils import get_node_character_indexes
from src.models.chunk import Chunk


class PythonChunker:
    """Split loaded Python source files into structure-aware chunks."""

    def __init__(self, max_chunk_size: int) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk(self, source_file: LoadedSourceFile) -> list[Chunk]:
        """Split one loaded Python source file into structured chunks."""
        syntax_tree = ast.parse(source_file.text)
        chunks: list[Chunk] = []

        for node in syntax_tree.body:
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                continue

            node_text = ast.get_source_segment(
                source_file.text,
                node,
            )
            if node_text is None:
                continue

            if len(node_text) <= self.max_chunk_size:
                chunks.append(
                    self._build_ast_chunk(
                        source_file,
                        node,
                        node_text,
                        self._node_chunk_type(node),
                    ),
                )
            else:
                chunks.extend(
                    self._chunk_oversized_node(
                        source_file,
                        node,
                    ),
                )

        return chunks

    def _chunk_oversized_node(
        self,
        source_file: LoadedSourceFile,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    ) -> list[Chunk]:
        """Split an oversized structural node by its child statements."""
        chunks: list[Chunk] = []

        for child in node.body:
            child_text = ast.get_source_segment(
                source_file.text,
                child,
            )
            if child_text is None:
                continue

            if len(child_text) <= self.max_chunk_size:
                chunks.append(
                    self._build_ast_chunk(
                        source_file,
                        child,
                        child_text,
                        type(child).__name__,
                    ),
                )
            else:
                chunks.extend(
                    self._split_oversized_child(
                        source_file,
                        child,
                        child_text,
                    ),
                )

        return chunks

    def _split_oversized_child(
        self,
        source_file: LoadedSourceFile,
        child: ast.stmt,
        child_text: str,
    ) -> list[Chunk]:
        """Split an oversized child by lines, then characters if needed."""
        chunks: list[Chunk] = []
        child_lines = child_text.splitlines(keepends=True)
        (
            current_piece_start,
            child_end_index,
        ) = get_node_character_indexes(
            source_file.text,
            child,
        )
        current_piece = ""

        for line in child_lines:
            if len(line) > self.max_chunk_size:
                if current_piece:
                    current_piece_end = (
                        current_piece_start
                        + len(current_piece)
                        - 1
                    )
                    chunks.append(
                        self._build_chunk(
                            source_file,
                            current_piece,
                            current_piece_start,
                            current_piece_end,
                            "line_fallback",
                        ),
                    )
                    current_piece_start = current_piece_end + 1
                    current_piece = ""

                chunks.extend(
                    self._split_raw_line(
                        source_file,
                        line,
                        current_piece_start,
                    ),
                )
                current_piece_start += len(line)

            elif (
                len(current_piece + line)
                > self.max_chunk_size
            ):
                current_piece_end = (
                    current_piece_start
                    + len(current_piece)
                    - 1
                )
                chunks.append(
                    self._build_chunk(
                        source_file,
                        current_piece,
                        current_piece_start,
                        current_piece_end,
                        "line_fallback",
                    ),
                )
                current_piece_start = current_piece_end + 1
                current_piece = line

            else:
                current_piece += line

        if current_piece:
            chunks.append(
                self._build_chunk(
                    source_file,
                    current_piece,
                    current_piece_start,
                    child_end_index,
                    "line_fallback",
                ),
            )

        return chunks

    def _split_raw_line(
        self,
        source_file: LoadedSourceFile,
        line: str,
        line_start_index: int,
    ) -> list[Chunk]:
        """Split one oversized line into raw character chunks."""
        chunks: list[Chunk] = []
        line_start = 0

        while line_start < len(line):
            raw_piece = line[
                line_start:line_start + self.max_chunk_size
            ]
            raw_piece_start = line_start_index + line_start
            raw_piece_end = (
                raw_piece_start
                + len(raw_piece)
                - 1
            )
            chunks.append(
                self._build_chunk(
                    source_file,
                    raw_piece,
                    raw_piece_start,
                    raw_piece_end,
                    "character_fallback",
                ),
            )
            line_start += len(raw_piece)

        return chunks

    def _build_ast_chunk(
        self,
        source_file: LoadedSourceFile,
        node: ast.stmt,
        text: str,
        chunk_type: str,
    ) -> Chunk:
        """Build a chunk using the exact indexes of an AST node."""
        first_char_index, last_char_index = (
            get_node_character_indexes(
                source_file.text,
                node,
            )
        )
        return self._build_chunk(
            source_file,
            text,
            first_char_index,
            last_char_index,
            chunk_type,
        )

    def _build_chunk(
        self,
        source_file: LoadedSourceFile,
        text: str,
        first_char_index: int,
        last_char_index: int,
        chunk_type: str,
    ) -> Chunk:
        """Build a chunk from text, indexes, and metadata."""
        return Chunk(
            text=text,
            file_path=str(source_file.path),
            first_character_index=first_char_index,
            last_character_index=last_char_index,
            file_type=source_file.file_type,
            chunk_type=chunk_type,
        )

    def _node_chunk_type(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    ) -> str:
        """Return the chunk type for a top-level structural node."""
        if isinstance(node, ast.FunctionDef):
            return "function"
        if isinstance(node, ast.AsyncFunctionDef):
            return "async_function"
        return "class"
