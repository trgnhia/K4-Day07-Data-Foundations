"""Chiến lược chunking cá nhân cho corpus chính sách Shopee dạng Markdown."""

from __future__ import annotations

import re


class HeadingSectionChunker:
    """Giữ tiêu đề Markdown cùng nội dung điều khoản/section phía sau nó.

    Chính sách Shopee đã được chuẩn hóa theo heading (``#``/``##``). Giữ heading
    trong chunk giúp embedding và người đọc biết điều kiện hay quy trình đang
    thuộc chính sách nào, thay vì cắt thuần theo số ký tự.
    """

    def __init__(self, chunk_size: int = 650) -> None:
        if chunk_size < 80:
            raise ValueError("chunk_size must be at least 80")
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = self._extract_sections(text)
        chunks: list[str] = []
        for section in sections:
            chunks.extend(self._split_section(section))
        return chunks

    def _extract_sections(self, text: str) -> list[str]:
        """Tạo section có nội dung; tiêu đề cấp 1 được làm ngữ cảnh cho cấp 2."""
        document_title = ""
        section_heading = ""
        body_lines: list[str] = []
        sections: list[str] = []

        def flush() -> None:
            nonlocal body_lines
            body = "\n".join(body_lines).strip()
            if not body:
                return
            headings = [heading for heading in (document_title, section_heading) if heading]
            sections.append("\n\n".join([*headings, body]))
            body_lines = []

        for line in text.strip().splitlines():
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if not match:
                body_lines.append(line)
                continue
            level = len(match.group(1))
            if level == 1:
                flush()
                document_title = line.strip()
                section_heading = ""
            else:
                flush()
                section_heading = line.strip()
        flush()
        return sections or [text.strip()]

    def _split_section(self, section: str) -> list[str]:
        if len(section) <= self.chunk_size:
            return [section]

        lines = section.splitlines()
        heading = lines[0] if lines and re.match(r"^#{1,6}\s+", lines[0]) else ""
        body = "\n".join(lines[1:]).strip() if heading else section
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", body) if paragraph.strip()]

        chunks: list[str] = []
        current = heading
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = heading
            # Một đoạn quá dài vẫn phải bảo đảm kích thước chunk.
            while len(paragraph) > self.chunk_size - len(heading) - 2:
                available = max(1, self.chunk_size - len(heading) - 2)
                piece, paragraph = paragraph[:available], paragraph[available:]
                chunks.append(f"{heading}\n\n{piece}".strip() if heading else piece)
            current = f"{heading}\n\n{paragraph}".strip() if heading else paragraph
        if current:
            chunks.append(current)
        return chunks
