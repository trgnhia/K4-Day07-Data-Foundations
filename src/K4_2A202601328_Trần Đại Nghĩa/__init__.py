"""Bài làm cá nhân của Trần Đại Nghĩa — MSSV 2A202601328."""

from .agent import KnowledgeBaseAgent
from .chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
    compute_similarity,
)
from .models import Document
from .store import EmbeddingStore
from .custom_chunker import HeadingSectionChunker
from ..embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    MockEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)

__all__ = [
    "Document", "FixedSizeChunker", "SentenceChunker", "RecursiveChunker",
    "ChunkingStrategyComparator", "compute_similarity", "EmbeddingStore",
    "KnowledgeBaseAgent", "MockEmbedder", "LocalEmbedder", "OpenAIEmbedder",
    "HeadingSectionChunker",
    "_mock_embed", "LOCAL_EMBEDDING_MODEL", "OPENAI_EMBEDDING_MODEL",
    "EMBEDDING_PROVIDER_ENV",
]
