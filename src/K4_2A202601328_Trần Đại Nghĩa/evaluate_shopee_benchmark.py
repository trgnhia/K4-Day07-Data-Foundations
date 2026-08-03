r"""Chạy benchmark cá nhân trên corpus Shopee bằng HeadingSectionChunker.

Chạy từ thư mục gốc trên PowerShell:

    $env:LAB_SOLUTION_PACKAGE='src.K4_2A202601328_Trần Đại Nghĩa'
    $env:PYTHONUTF8='1'
    python 'src\K4_2A202601328_Trần Đại Nghĩa\evaluate_shopee_benchmark.py'
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

# Khi chạy file trực tiếp, Python chỉ thêm thư mục file này vào sys.path.
# Bổ sung thư mục gốc của repo để import được ingest.py và package src.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingest import chunk_document, load_documents
from src.embeddings import LocalEmbedder


CORPUS_DIR = "data/shopee_ecommerce"
BENCHMARKS = [
    {
        "id": 1,
        "query": "Những lý do nào khiến Người mua có thể yêu cầu Trả hàng hoặc Hoàn tiền?",
        "expected_doc_id": "shopee-return-conditions",
        "metadata_filter": None,
    },
    {
        "id": 2,
        "query": "Người mua cần chuẩn bị và gửi bằng chứng trả hàng hoặc hoàn tiền như thế nào?",
        "expected_doc_id": "shopee-return-request-process",
        "metadata_filter": None,
    },
    {
        "id": 3,
        "query": "Khi nào Người mua không thể chọn COD và cần làm gì?",
        "expected_doc_id": "shopee-cod-eligibility",
        "metadata_filter": None,
    },
    {
        "id": 4,
        "query": "Người bán phải mô tả sản phẩm như thế nào khi đăng bán?",
        "expected_doc_id": "shopee-seller-listing-policy",
        "metadata_filter": {"customer_role": "seller"},
    },
    {
        "id": 5,
        "query": "Vi phạm chính sách hàng cấm hoặc hạn chế có thể bị xử lý ra sao?",
        "expected_doc_id": "shopee-prohibited-products-policy",
        "metadata_filter": {"customer_role": "seller"},
    },
]


def extractive_demo_llm(prompt: str) -> str:
    """Demo LLM có căn cứ: trả lại đoạn ngữ cảnh đứng đầu để kiểm tra grounding.

    Hàm này không tự tạo thông tin mới. Khi nhóm có LLM được phép dùng, thay hàm
    này bằng adapter tương ứng và giữ nguyên benchmark/retrieval.
    """
    context = prompt.split("Ngữ cảnh:\n", 1)[-1].split("\n\nCâu hỏi:", 1)[0]
    return context[:500].replace("\n", " ")


def main() -> None:
    package_name = os.environ.get("LAB_SOLUTION_PACKAGE", f"src.{Path(__file__).parent.name}")
    package = importlib.import_module(package_name)

    chunker = package.HeadingSectionChunker(chunk_size=650)
    chunks = [
        chunk
        for document in load_documents(CORPUS_DIR)
        for chunk in chunk_document(document, chunker)
    ]
    embedder = LocalEmbedder()
    store = package.EmbeddingStore("nghia_shopee_heading_sections", embedding_fn=embedder)
    store.add_documents(chunks)
    agent = package.KnowledgeBaseAgent(store, extractive_demo_llm)

    print("# Kết quả benchmark — HeadingSectionChunker")
    print(f"- Corpus: {CORPUS_DIR}; documents: 8; chunks: {len(chunks)}")
    print(f"- Embedder: {embedder._backend_name}")
    print("- Strategy: HeadingSectionChunker(chunk_size=650)")
    print()
    print("| # | Query | Filter | Top-3 (doc_id: score) | Relevant trong top-3? | Agent answer (preview) |")
    print("|---|---|---|---|---|---|")

    for item in BENCHMARKS:
        if item["metadata_filter"]:
            results = store.search_with_filter(item["query"], top_k=3, metadata_filter=item["metadata_filter"])
            filter_text = "customer_role=seller"
        else:
            results = store.search(item["query"], top_k=3)
            filter_text = "—"
        top3 = "; ".join(f"{result['metadata']['doc_id']}: {result['score']:.3f}" for result in results)
        relevant = any(result["metadata"]["doc_id"] == item["expected_doc_id"] for result in results)
        answer = agent.answer(item["query"], top_k=3, metadata_filter=item["metadata_filter"]).replace("|", "/")[:170]
        print(f"| {item['id']} | {item['query']} | {filter_text} | {top3} | {'Có' if relevant else 'Không'} | {answer} |")


if __name__ == "__main__":
    main()
