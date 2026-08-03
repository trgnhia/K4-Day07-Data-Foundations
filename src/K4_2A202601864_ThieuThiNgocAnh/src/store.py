from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """Small in-memory vector store with metadata pre-filtering."""

    def __init__(self, collection_name: str = "documents", embedding_fn: Callable[[str], list[float]] | None = None) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._store: list[dict[str, Any]] = []
        self._next_index = 0

    def _make_record(self, doc: Document) -> dict[str, Any]:
        record = {
            "id": f"{doc.id}::{self._next_index}",
            "document_id": doc.id,
            "content": doc.content,
            "metadata": dict(doc.metadata),
            "embedding": [float(value) for value in self._embedding_fn(doc.content)],
        }
        record["metadata"].setdefault("doc_id", doc.id)
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0:
            return []
        query_embedding = self._embedding_fn(query)
        ranked = sorted(records, key=lambda record: _dot(query_embedding, record["embedding"]), reverse=True)
        return [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": dict(record["metadata"]),
                "score": _dot(query_embedding, record["embedding"]),
            }
            for record in ranked[:top_k]
        ]

    def add_documents(self, docs: list[Document]) -> None:
        self._store.extend(self._make_record(doc) for doc in docs)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict | None = None) -> list[dict]:
        if not metadata_filter:
            return self.search(query, top_k)
        candidates = [
            record for record in self._store
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        original_size = len(self._store)
        self._store = [
            record for record in self._store
            if record["metadata"].get("doc_id", record["document_id"]) != doc_id
        ]
        return len(self._store) < original_size
