from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            context = "Không tìm thấy ngữ cảnh liên quan trong cơ sở tri thức."
        else:
            context = "\n\n".join(
                f"[Nguồn {index} | doc_id={item['metadata'].get('doc_id', item['id'])}]\n{item['content']}"
                for index, item in enumerate(results, start=1)
            )
        prompt = (
            "Bạn là trợ lý hỏi đáp dựa trên cơ sở tri thức. Chỉ sử dụng NGỮ CẢNH bên dưới; "
            "nếu ngữ cảnh không đủ, hãy nói rõ là không đủ thông tin. Không tự suy đoán.\n\n"
            f"NGỮ CẢNH:\n{context}\n\nCÂU HỎI: {question}\n\nTRẢ LỜI:"
        )
        return self.llm_fn(prompt)
