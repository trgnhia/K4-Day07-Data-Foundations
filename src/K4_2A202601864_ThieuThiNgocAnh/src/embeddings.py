from __future__ import annotations

import hashlib
import math


class MockEmbedder:
    """Deterministic, normalized embeddings for tests and offline demos."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def __call__(self, text: str) -> list[float]:
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        vector: list[float] = []
        for _ in range(self.dim):
            seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
            vector.append((seed / 0xFFFFFFFF) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


_mock_embed = MockEmbedder()
