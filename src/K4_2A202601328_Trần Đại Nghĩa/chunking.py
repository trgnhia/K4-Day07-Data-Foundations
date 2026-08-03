from __future__ import annotations

import math
import re


class FixedSizeChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        if chunk_size < 1:
            raise ValueError("chunk_size phải lớn hơn 0")
        if not 0 <= overlap < chunk_size:
            raise ValueError("overlap phải từ 0 đến nhỏ hơn chunk_size")
        self.chunk_size, self.overlap = chunk_size, overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        step = self.chunk_size - self.overlap
        return [text[start : start + self.chunk_size] for start in range(0, len(text), step)
                if start == 0 or start < len(text)] if len(text) > self.chunk_size else [text]


class SentenceChunker:
    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text.strip()) if sentence.strip()]
        return [" ".join(sentences[index:index + self.max_sentences_per_chunk])
                for index in range(0, len(sentences), self.max_sentences_per_chunk)]


class RecursiveChunker:
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        if chunk_size < 1:
            raise ValueError("chunk_size phải lớn hơn 0")
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return [piece.strip() for piece in self._split(text, self.separators) if piece.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [current_text[index:index + self.chunk_size]
                    for index in range(0, len(current_text), self.chunk_size)]
        separator = remaining_separators[0]
        if not separator:
            return [current_text[index:index + self.chunk_size]
                    for index in range(0, len(current_text), self.chunk_size)]
        parts = current_text.split(separator)
        chunks: list[str] = []
        buffer = ""
        for part in parts:
            candidate = part if not buffer else buffer + separator + part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.extend(self._split(buffer, remaining_separators[1:]))
            if len(part) > self.chunk_size:
                chunks.extend(self._split(part, remaining_separators[1:]))
                buffer = ""
            else:
                buffer = part
        if buffer:
            chunks.extend(self._split(buffer, remaining_separators[1:]))
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }
        result = {}
        for name, strategy in strategies.items():
            chunks = strategy.chunk(text)
            result[name] = {
                "count": len(chunks),
                "avg_length": sum(map(len, chunks)) / len(chunks) if chunks else 0.0,
                "chunks": chunks,
            }
        return result
