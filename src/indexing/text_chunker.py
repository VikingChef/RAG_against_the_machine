"""Split Markdown and plain-text source files into semantic chunks."""

from src.indexing.index_models import LoadedSourceFile
from src.models.chunk import Chunk


class _TextBlock:
    """Represent one semantic text block by its source indexes."""

    def __init__(
        self,
        start_index: int,
        end_index: int,
        block_type: str,
        section_id: int,
    ) -> None:
        """Initialize one semantic text block."""
        self.start_index = start_index
        self.end_index = end_index
        self.block_type = block_type
        self.section_id = section_id


class TextChunker:
    """Split loaded text source files while preserving semantic structure."""

    def __init__(
        self,
        max_chunk_size: int,
        overlap: int,
    ) -> None:
        """Initialize the text chunker with size and overlap limits."""
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(
        self,
        source_file: LoadedSourceFile,
    ) -> list[Chunk]:
        """Split one loaded text source file into structured chunks."""
        if not source_file.text.strip():
            return []

        if source_file.file_type == ".md":
            blocks = self._parse_markdown_blocks(
                text=source_file.text,
            )
        else:
            blocks = self._parse_text_blocks(
                text=source_file.text,
            )

        grouped_blocks = self._group_blocks(blocks)
        split_blocks = []

        for block in grouped_blocks:
            split_blocks.extend(
                self._split_oversized_block(
                    block,
                    source_file.text,
                )
            )

        overlapped_blocks = self._apply_overlap(split_blocks)
        final_chunks: list[Chunk] = []

        for block in overlapped_blocks:
            final_chunks.append(
                self._build_chunk(
                    source_file,
                    block,
                )
            )

        return final_chunks

    def _parse_text_blocks(
        self,
        text: str,
    ) -> list[_TextBlock]:
        """Identify paragraph boundaries in plain-text source."""

        lines = text.splitlines(keepends=True)
        blocks: list[_TextBlock] = []
        current_block_start: int | None = None
        position = 0

        for line in lines:
            if line.strip() == "":
                if current_block_start is not None:
                    blocks.append(
                        _TextBlock(
                            start_index=current_block_start,
                            end_index=position - 1,
                            block_type="paragraph",
                            section_id=0,
                        ),
                    )
                current_block_start = None
            else:
                if current_block_start is None:
                    current_block_start = position

            position += len(line)

        if current_block_start is not None:
            blocks.append(
                _TextBlock(
                    start_index=current_block_start,
                    end_index=len(text) - 1,
                    block_type="paragraph",
                    section_id=0,
                ),
            )

        return blocks

    def _parse_markdown_blocks(
        self,
        text: str,
    ) -> list[_TextBlock]:
        """Parse Markdown source into ordered semantic text blocks."""

        lines = text.splitlines(keepends=True)
        blocks: list[_TextBlock] = []
        section_id = 0
        line_index = 0
        position = 0

        while line_index < len(lines):
            block_type = self._detect_markdown_block_type(
                lines=lines,
                line_index=line_index,
            )

            if block_type == "blank":
                position += len(lines[line_index])
                line_index += 1
                continue

            (
                block,
                line_index,
                position,
                section_id,
            ) = self._consume_markdown_block(
                block_type=block_type,
                lines=lines,
                start_line_index=line_index,
                start_position=position,
                section_id=section_id,
            )
            blocks.append(block)

        return blocks

    def _detect_markdown_block_type(
        self,
        lines: list[str],
        line_index: int,
    ) -> str:
        """Identify the Markdown structure starting at one source line."""

        stripped_line = lines[line_index].strip()

        if stripped_line.startswith(("```", "~~~")):
            return "code_fence"

        if self._is_atx_heading(stripped_line):
            return "atx_heading"

        if self._is_setext_heading(
            lines=lines,
            line_index=line_index,
        ):
            return "setext_heading"

        if stripped_line == "":
            return "blank"

        if self._is_list_item(stripped_line):
            return "list"

        if self._is_blockquote(stripped_line):
            return "blockquote"

        return "paragraph"

    def _is_atx_heading(
        self,
        stripped_line: str,
    ) -> bool:
        """Return whether one stripped line is an ATX heading."""

        heading_level = 0

        for character in stripped_line:
            if character == "#":
                heading_level += 1
            else:
                break

        if not 1 <= heading_level <= 6:
            return False

        if heading_level == len(stripped_line):
            return True

        return stripped_line[heading_level].isspace()

    def _is_setext_heading(
        self,
        lines: list[str],
        line_index: int,
    ) -> bool:
        """Return whether two source lines form a Setext heading."""

        if (line_index + 1) >= len(lines):
            return False

        stripped_line = lines[line_index].strip()
        next_line_stripped = lines[line_index + 1].strip()

        if not stripped_line or not next_line_stripped:
            return False

        return (
            next_line_stripped.strip("=") == ""
            or next_line_stripped.strip("-") == ""
        )

    def _is_list_item(
        self,
        stripped_line: str,
    ) -> bool:
        """Return whether one stripped line is a Markdown list item."""

        if stripped_line.startswith(("- ", "* ", "+ ")):
            return True

        dot_index = stripped_line.find(".")

        if dot_index == -1:
            return False

        if dot_index + 1 >= len(stripped_line):
            return False

        if stripped_line[dot_index + 1] != " ":
            return False

        number_part = stripped_line[:dot_index]

        if number_part.isdigit():
            return True

        return False

    def _is_blockquote(
        self,
        stripped_line: str,
    ) -> bool:
        """Return whether one stripped line is a Markdown blockquote."""

        return stripped_line.startswith(">")

    def _consume_markdown_block(
        self,
        block_type: str,
        lines: list[str],
        start_line_index: int,
        start_position: int,
        section_id: int,
    ) -> tuple[_TextBlock, int, int, int]:
        """Route one detected Markdown structure to its consumer."""

        if block_type == "code_fence":
            return self._consume_fenced_code(
                lines=lines,
                start_line_index=start_line_index,
                start_position=start_position,
                section_id=section_id,
            )

        if block_type == "atx_heading":
            return self._consume_atx_heading(
                lines=lines,
                start_line_index=start_line_index,
                start_position=start_position,
                section_id=section_id,
            )

        if block_type == "list":
            return self._consume_list(
                lines=lines,
                start_line_index=start_line_index,
                start_position=start_position,
                section_id=section_id,
            )

        if block_type == "blockquote":
            return self._consume_blockquote(
                lines=lines,
                start_line_index=start_line_index,
                start_position=start_position,
                section_id=section_id,
            )

        if block_type == "paragraph":
            return self._consume_paragraph(
                lines=lines,
                start_line_index=start_line_index,
                start_position=start_position,
                section_id=section_id,
            )

        if block_type == "setext_heading":
            return self._consume_setext_heading(
                lines=lines,
                start_line_index=start_line_index,
                start_position=start_position,
                section_id=section_id,
            )

        raise ValueError(f"Unsupported block type: {block_type}")

    def _consume_fenced_code(
        self,
        lines: list[str],
        start_line_index: int,
        start_position: int,
        section_id: int,
    ) -> tuple[_TextBlock, int, int, int]:
        """Consume one fenced Markdown code block."""

        opening_line = lines[start_line_index].strip()

        if opening_line.startswith("```"):
            fence_marker = "```"
        else:
            fence_marker = "~~~"

        line_index = start_line_index
        position = start_position

        while line_index < len(lines):
            line = lines[line_index]
            stripped_line = line.strip()

            position += len(line)
            line_index += 1

            if (
                line_index - 1 != start_line_index
                and stripped_line.startswith(fence_marker)
            ):
                break

        block = _TextBlock(
            start_index=start_position,
            end_index=position - 1,
            block_type="code_fence",
            section_id=section_id,
        )

        return block, line_index, position, section_id

    def _consume_atx_heading(
        self,
        lines: list[str],
        start_line_index: int,
        start_position: int,
        section_id: int,
    ) -> tuple[_TextBlock, int, int, int]:
        """Consume one ATX Markdown heading block."""

        new_section_id = section_id + 1
        heading_line = lines[start_line_index]
        heading_end = start_position + len(heading_line) - 1
        next_line_index = start_line_index + 1
        next_position = start_position + len(heading_line)

        block = _TextBlock(
            start_index=start_position,
            end_index=heading_end,
            block_type="heading",
            section_id=new_section_id,
        )

        return block, next_line_index, next_position, new_section_id

    def _consume_setext_heading(
        self,
        lines: list[str],
        start_line_index: int,
        start_position: int,
        section_id: int,
    ) -> tuple[_TextBlock, int, int, int]:
        """Consume one Setext Markdown heading block."""

        new_section_id = section_id + 1
        heading_line = lines[start_line_index]
        underline_line = lines[start_line_index + 1]

        heading_end = (
            start_position
            + len(heading_line)
            + len(underline_line)
            - 1
        )
        next_line_index = start_line_index + 2
        next_position = (
            start_position
            + len(heading_line)
            + len(underline_line)
        )

        block = _TextBlock(
            start_index=start_position,
            end_index=heading_end,
            block_type="heading",
            section_id=new_section_id,
        )

        return block, next_line_index, next_position, new_section_id

    def _consume_list(
        self,
        lines: list[str],
        start_line_index: int,
        start_position: int,
        section_id: int,
    ) -> tuple[_TextBlock, int, int, int]:
        """Consume one consecutive Markdown list block."""

        line_index = start_line_index
        position = start_position

        while (
            line_index < len(lines)
            and self._is_list_item(lines[line_index].strip())
        ):
            line = lines[line_index]
            position += len(line)
            line_index += 1

        block = _TextBlock(
            start_index=start_position,
            end_index=position - 1,
            block_type="list",
            section_id=section_id,
        )

        return block, line_index, position, section_id

    def _consume_blockquote(
        self,
        lines: list[str],
        start_line_index: int,
        start_position: int,
        section_id: int,
    ) -> tuple[_TextBlock, int, int, int]:
        """Consume one consecutive Markdown blockquote block."""

        line_index = start_line_index
        position = start_position

        while (
            line_index < len(lines)
            and self._is_blockquote(lines[line_index].strip())
        ):
            line = lines[line_index]
            position += len(line)
            line_index += 1

        block = _TextBlock(
            start_index=start_position,
            end_index=position - 1,
            block_type="blockquote",
            section_id=section_id,
        )

        return block, line_index, position, section_id

    def _consume_paragraph(
        self,
        lines: list[str],
        start_line_index: int,
        start_position: int,
        section_id: int,
    ) -> tuple[_TextBlock, int, int, int]:
        """Consume one consecutive Markdown paragraph block."""

        line_index = start_line_index
        position = start_position

        while (
            line_index < len(lines)
            and self._detect_markdown_block_type(
                lines=lines,
                line_index=line_index,
            ) == "paragraph"
        ):
            line = lines[line_index]
            position += len(line)
            line_index += 1

        block = _TextBlock(
            start_index=start_position,
            end_index=position - 1,
            block_type="paragraph",
            section_id=section_id,
        )

        return block, line_index, position, section_id

    def _group_blocks(
        self,
        blocks: list[_TextBlock],
    ) -> list[_TextBlock]:
        """Group adjacent text blocks into chunk-sized source ranges."""

        if not blocks:
            return []

        grouped_blocks: list[_TextBlock] = []
        current_start = blocks[0].start_index
        current_end = blocks[0].end_index
        current_section = blocks[0].section_id
        current_type = blocks[0].block_type

        for block in blocks[1:]:
            if (
                block.section_id == current_section
                and (
                    block.end_index
                    - current_start
                    + 1
                    <= self.max_chunk_size
                )
            ):
                current_end = block.end_index
                current_type = "group"
            else:
                grouped_block = _TextBlock(
                    start_index=current_start,
                    end_index=current_end,
                    block_type=current_type,
                    section_id=current_section,
                )
                grouped_blocks.append(grouped_block)

                current_start = block.start_index
                current_end = block.end_index
                current_section = block.section_id
                current_type = block.block_type

        grouped_block = _TextBlock(
            start_index=current_start,
            end_index=current_end,
            block_type=current_type,
            section_id=current_section,
        )
        grouped_blocks.append(grouped_block)

        return grouped_blocks

    def _split_oversized_block(
        self,
        block: _TextBlock,
        text: str,
    ) -> list[_TextBlock]:
        """Split one oversized text block while preserving source indexes."""

        if (
            block.end_index
            - block.start_index
            + 1
            <= self.max_chunk_size
        ):
            return [block]

        block_text = text[
            block.start_index:block.end_index + 1
        ]
        lines = block_text.splitlines(keepends=True)

        split_blocks: list[_TextBlock] = []
        position = block.start_index
        current_start = block.start_index
        current_length = 0

        for line in lines:
            current_line_length = len(line)

            if current_line_length > self.max_chunk_size:
                if current_length > 0:
                    split_blocks.append(
                        _TextBlock(
                            start_index=current_start,
                            end_index=position - 1,
                            block_type="line_fallback",
                            section_id=block.section_id,
                        ),
                    )
                    current_length = 0

                split_blocks.extend(
                    self._split_oversized_line(
                        start_position=position,
                        line_length=current_line_length,
                        section_id=block.section_id,
                    ),
                )

                position += current_line_length
                current_start = position
                continue

            if (
                current_length
                + current_line_length
                <= self.max_chunk_size
            ):
                current_length += current_line_length
                position += current_line_length
                continue

            split_blocks.append(
                _TextBlock(
                    start_index=current_start,
                    end_index=position - 1,
                    block_type="line_fallback",
                    section_id=block.section_id,
                ),
            )

            current_start = position
            current_length = current_line_length
            position += current_line_length

        if current_length > 0:
            split_blocks.append(
                _TextBlock(
                    start_index=current_start,
                    end_index=position - 1,
                    block_type="line_fallback",
                    section_id=block.section_id,
                ),
            )

        return split_blocks

    def _split_oversized_line(
        self,
        start_position: int,
        line_length: int,
        section_id: int,
    ) -> list[_TextBlock]:
        """Split one oversized source line into character-sized ranges."""

        split_blocks: list[_TextBlock] = []
        position = start_position
        remaining_length = line_length

        while remaining_length > 0:
            piece_length = min(
                self.max_chunk_size,
                remaining_length,
            )
            end_index = position + piece_length - 1

            split_blocks.append(
                _TextBlock(
                    start_index=position,
                    end_index=end_index,
                    block_type="character_fallback",
                    section_id=section_id,
                ),
            )

            position += piece_length
            remaining_length -= piece_length

        return split_blocks

    def _apply_overlap(
        self,
        blocks: list[_TextBlock],
    ) -> list[_TextBlock]:
        """Apply source-index overlap without crossing section boundaries."""

        if not blocks:
            return []

        overlapped_blocks: list[_TextBlock] = [blocks[0]]

        for index in range(1, len(blocks)):
            current_block = blocks[index]
            previous_block = blocks[index - 1]
            if current_block.section_id == previous_block.section_id:
                current_block_size = (
                    current_block.end_index
                    - current_block.start_index
                    + 1
                )
                spare_room = self.max_chunk_size - current_block_size
                overlap = min(self.overlap, spare_room)
                previous_block_size = (
                    previous_block.end_index
                    - previous_block.start_index
                    + 1
                )
                actual_overlap = min(
                    overlap,
                    previous_block_size
                )
                new_start = current_block.start_index - actual_overlap
                overlapped_blocks.append(
                    _TextBlock(
                        start_index=new_start,
                        end_index=current_block.end_index,
                        block_type=current_block.block_type,
                        section_id=current_block.section_id,
                    )
                )
            else:
                overlapped_blocks.append(current_block)

        return overlapped_blocks

    def _build_chunk(
        self,
        source_file: LoadedSourceFile,
        block: _TextBlock,
    ) -> Chunk:
        """Build one final Chunk from a finalized text block."""

        chunk_text = source_file.text[
            block.start_index:block.end_index + 1
        ]

        if block.block_type == "line_fallback":
            chunk_type = "line_fallback"
        elif block.block_type == "character_fallback":
            chunk_type = "character_fallback"
        elif source_file.file_type == ".md":
            chunk_type = "markdown"
        else:
            chunk_type = "text"

        return Chunk(
            file_path=str(source_file.path),
            text=chunk_text,
            first_character_index=block.start_index,
            last_character_index=block.end_index,
            file_type=source_file.file_type,
            chunk_type=chunk_type,
        )
