from __future__ import annotations

import sys
from pathlib import Path
from statistics import mean

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest import build_knowledge_base
from src.chunking import FixedSizeChunker
from src.embeddings import LocalEmbedder, _mock_embed


DATA_DIR = ROOT / "data" / "shopee_ecommerce"
BASELINE_CHUNKER = FixedSizeChunker(chunk_size=400, overlap=50)
MEMBER5_CHUNKER = FixedSizeChunker(chunk_size=700, overlap=100)
QUERIES = [
    "Shopee quy định như thế nào về hoàn tiền khi đơn hàng bị lỗi?",
    "Điều kiện nào khiến Shopee từ chối yêu cầu trả hàng?",
    "Làm sao để người bán biết được tiêu chuẩn đăng bán sản phẩm trên Shopee?",
    "Seller phải làm gì nếu khách hàng yêu cầu đổi trả?",
    "Seller cần chuẩn bị gì để đảm bảo đơn hàng được giao thành công?",
]
SELLER_FILTER = {"customer_role": "seller"}


def load_store(chunker, description: str):
    print(f"\n---\nBuilding store for {description}")
    try:
        embedder = LocalEmbedder()
    except Exception as exc:
        print("Warning: LocalEmbedder is not available. Falling back to mock embedder.")
        print(exc)
        embedder = _mock_embed

    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
    size = store.get_collection_size()
    print(f"Loaded {size} chunks into EmbeddingStore")
    return store


def print_query_results(store, query: str, top_k: int = 3):
    print(f"\nQuery: {query}")
    results = store.search(query, top_k=top_k)
    for index, result in enumerate(results, start=1):
        score = result["score"]
        metadata = result.get("metadata", {})
        snippet = result["content"].replace("\n", " ")[:200]
        print(f"  {index}. score={score:.4f} doc_id={metadata.get('doc_id')} source={metadata.get('source')}")
        print(f"      {snippet}")
    return results


def print_filtered_results(store, query: str, top_k: int = 3):
    print(f"\nFiltered (seller) Query: {query}")
    results = store.search_with_filter(query, top_k=top_k, metadata_filter=SELLER_FILTER)
    if not results:
        print("  No chunks matched seller filter.")
        return results
    for index, result in enumerate(results, start=1):
        score = result["score"]
        metadata = result.get("metadata", {})
        snippet = result["content"].replace("\n", " ")[:200]
        print(f"  {index}. score={score:.4f} doc_id={metadata.get('doc_id')} source={metadata.get('source')}")
        print(f"      {snippet}")
    return results


def summarize_chunks(store, description: str):
    contents = [record["content"] for record in store._store]
    lengths = [len(text) for text in contents if text]
    print(f"\n{description} chunk stats:")
    print(f"  chunk count: {len(lengths)}")
    print(f"  avg_length: {mean(lengths):.1f}" if lengths else "  no chunks")
    print(f"  min_length: {min(lengths):.1f}" if lengths else "")
    print(f"  max_length: {max(lengths):.1f}" if lengths else "")


def main() -> None:
    if not DATA_DIR.exists():
        raise SystemExit(f"Corpus not found: {DATA_DIR}")

    baseline_store = load_store(BASELINE_CHUNKER, "baseline FixedSize(400,50)")
    member5_store = load_store(MEMBER5_CHUNKER, "member5 FixedSize(700,100)")

    summarize_chunks(baseline_store, "Baseline")
    summarize_chunks(member5_store, "Member5")

    for idx, query in enumerate(QUERIES, start=1):
        print(f"\n=== Query {idx} ===")
        print("[Baseline results]")
        print_query_results(baseline_store, query)
        print("[Member5 results]")
        print_query_results(member5_store, query)

        if idx >= 4:
            print("[Baseline seller-filtered]")
            print_filtered_results(baseline_store, query)
            print("[Member5 seller-filtered]")
            print_filtered_results(member5_store, query)


if __name__ == "__main__":
    main()
