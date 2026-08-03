from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict | None = None) -> str:
        results = (
            self.store.search_with_filter(question, top_k=top_k, metadata_filter=metadata_filter)
            if metadata_filter
            else self.store.search(question, top_k=top_k)
        )
        context = "\n\n".join(
            f"[Nguồn {index}] {result['content']}" for index, result in enumerate(results, start=1)
        ) or "Không tìm thấy ngữ cảnh liên quan."
        prompt = (
            "Trả lời câu hỏi chỉ dựa trên ngữ cảnh bên dưới. Nếu thiếu thông tin, hãy nói rõ.\n\n"
            f"Ngữ cảnh:\n{context}\n\nCâu hỏi: {question}\nTrả lời:"
        )
        return self.llm_fn(prompt)
