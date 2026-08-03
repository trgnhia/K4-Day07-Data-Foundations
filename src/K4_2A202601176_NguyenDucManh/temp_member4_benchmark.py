import os
from ingest import build_knowledge_base
from src.chunking import FixedSizeChunker
from src.embeddings import LocalEmbedder

os.environ["EMBEDDING_PROVIDER"] = "local"
os.environ["LAB_DATA_DIR"] = "data/shopee_ecommerce"

embedder = LocalEmbedder()
chunker = FixedSizeChunker(chunk_size=400, overlap=50)

store = build_knowledge_base(
    "data/shopee_ecommerce",
    embedding_fn=embedder,
    chunker=chunker,
    collection_name="member4_fixed_baseline",
)

print("Số chunk:", store.get_collection_size())

queries = [
    "Người mua có thể yêu cầu trả hàng/hoàn tiền khi nào?",
    "Người mua cần chuẩn bị những bằng chứng gì để gửi yêu cầu trả hàng/hoàn tiền?",
    "Khi nào người mua không thể chọn phương thức thanh toán COD?",
    "Người bán cần mô tả sản phẩm như thế nào khi đăng bán?",
    "Nếu người bán vi phạm chính sách hàng cấm/hạn chế thì có thể bị xử lý thế nào?",
]

for q in queries:
    print("\n=== QUERY ===")
    print(q)
    results = store.search(q, top_k=3)
    for i, r in enumerate(results, 1):
        print(f"{i}. score={r['score']:.3f} | doc_id={r['metadata'].get('doc_id')}")
        print(r['content'][:400].replace('\n', ' '))
        print("-" * 80)

seller_filter = {"customer_role": "seller"}
print("\n=== SELLER FILTERED QUERIES ===")
for q in queries[3:]:
    print("\nQUERY:", q)
    results = store.search_with_filter(q, top_k=3, metadata_filter=seller_filter)
    for i, r in enumerate(results, 1):
        print(f"{i}. score={r['score']:.3f} | doc_id={r['metadata'].get('doc_id')}")
        print(r['content'][:400].replace('\n', ' '))
        print("-" * 80)
