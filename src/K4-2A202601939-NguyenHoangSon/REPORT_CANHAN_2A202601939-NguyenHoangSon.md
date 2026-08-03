# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hoàng Sơn
**Mã sinh viên:** 2A202601939
**Nhóm:** noname
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (gần 1.0) nghĩa là góc giữa hai vector biểu diễn văn bản trong không gian embedding rất nhỏ, phản ánh hai đoạn văn bản có sự tương đồng cao về mặt ý nghĩa và bối cảnh ngữ nghĩa (semantic context), bất kể độ dài của chúng.

**Ví dụ có độ tương tự CAO:**
- Câu A: Chính sách đổi trả sản phẩm được áp dụng trong vòng 7 ngày kể từ khi nhận hàng.
- Câu B: Khách hàng có quyền hoàn trả mặt hàng đã mua trong thời hạn một tuần.
- Tại sao tương đồng: Cả hai câu đều diễn đạt cùng một quy định thương mại (trả hàng trong vòng 7 ngày / 1 tuần) nên hướng vector ngữ nghĩa trùng khớp nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Chính sách đổi trả sản phẩm được áp dụng trong vòng 7 ngày kể từ khi nhận hàng.
- Câu B: Máy chủ cơ sở dữ liệu hệ thống đã hoàn tất sao lưu định kỳ vào lúc 0 giờ.
- Tại sao khác: Câu A thuộc mảng chính sách mua sắm, câu B thuộc mảng vận hành hạ tầng CNTT; không gian ngữ nghĩa hoàn toàn khác nhau nên góc giữa hai vector gần như vuông góc ($cos \approx 0$).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid bị ảnh hưởng mạnh bởi độ dài văn bản (chuẩn magnitude của vector), làm cho hai câu cùng ý nghĩa nhưng khác độ dài bị coi là distant. Ngược lại, Cosine similarity loại bỏ ảnh hưởng của độ dài bằng cách chỉ đo hướng góc giữa hai vector, giúp đánh giá chính xác độ tương đồng về mặt ý nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Bước nhảy giữa các chunk: $step = chunk\_size - overlap = 500 - 50 = 450$ (ký tự).
> Công thức tính số lượng chunk:
> $$\text{Số lượng chunk} = \left\lceil \frac{\text{độ dài} - \text{overlap}}{\text{chunk\_size} - \text{overlap}} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \left\lceil 22.111 \right\rceil = 23$$
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước nhảy giảm còn $500 - 100 = 400$, số lượng chunk tăng lên $\lceil \frac{10000 - 100}{400} \rceil = \lceil 24.75 \rceil = 25$ chunks (tăng 2 chunks). Tăng overlap giúp giữ nguyên bối cảnh ở các điểm ranh giới cắt, tránh việc chia cắt làm mất ngữ nghĩa của các câu nằm ngay điểm cắt.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy `re.split(r'(?<=[.!?])\s+|\n+', text)` để phân tách văn bản thành danh sách câu dựa theo các dấu kết thúc câu và dấu xuống dòng. Gom tối đa `max_sentences_per_chunk` câu liên tiếp thành từng chunk và làm sạch khoảng trắng thừa. Xử lý trường hợp ngoại lệ văn bản rỗng hoặc chỉ chứa khoảng trắng bằng cách trả về `[]`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng danh sách phân tách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Nếu đoạn văn bản hiện tại $\le chunk\_size$, đây là trường hợp cơ sở (base case) và trả về đoạn đó. Ngược lại, thử phân tách bằng separator ưu tiên cao nhất; nếu các đoạn nhỏ vẫn vượt kích thước cho phép, hàm sẽ đệ quy gọi `_split` trên danh sách separator còn lại.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Trong `add_documents`, mỗi `Document` được tạo bản ghi normalized chứa `id`, `content`, `metadata` và vector `embedding` được tạo ra từ `_embedding_fn`. Hàm `search` nhúng truy vấn thành vector, tính tích vô hướng (`_dot`) giữa vector truy vấn và từng vector trong store, sau đó sắp xếp giảm dần theo điểm `score` và lấy `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` thực hiện lọc trước (pre-filtering): duyệt các bản ghi và giữ lại các đoạn có `metadata` khớp hoàn toàn với cặp key-value trong `metadata_filter`, rồi mới tính tương đồng vector trên tập lọc. `delete_document` loại bỏ tất cả các chunk có `id` hoặc `metadata['doc_id']` khớp với `doc_id` được yêu cầu, trả về `True` nếu có ít nhất 1 chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Gọi `store.search(question, top_k)` để truy xuất $k$ đoạn văn bản liên quan nhất. Nối nội dung các đoạn này thành một đoạn bối cảnh `context`, sau đó ghép vào prompt dạng:
> `Context:\n{context}\n\nQuestion: {question}\n\nAnswer:`
> và truyền vào hàm `llm_fn` để sinh câu trả lời RAG.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.10.0, pytest-9.1.1, pluggy-1.6.0
rootdir: F:\Vinuni\lab\K4-Day07-Data-Foundations
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.09s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Khách hàng được đổi trả trong 7 ngày | Thời hạn hoàn trả sản phẩm là một tuần | cao | 1.000 | Đúng |
| 2 | Người bán phải xác nhận đơn trong 24h | Người bán cần duyệt đơn hàng trong 1 ngày | cao | 1.000 | Đúng |
| 3 | Thời gian giao hàng dự kiến 3-5 ngày | Máy chủ ứng dụng đã khởi động lại | thấp | 0.000 | Đúng |
| 4 | Người mua kiểm tra hàng trước khi nhận | Người bán đóng gói hàng theo tiêu chuẩn | thấp | 0.450 | Đúng |
| 5 | Phương thức thanh toán chuyển khoản qua ngân hàng | Hỗ trợ thanh toán thẻ ATM nội địa | cao | 0.880 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả ở Cặp 4 gây bất ngờ vì dù cả hai câu đều đề cập đến quy trình mua bán thương mại điện tử nhưng vẫn có điểm số vừa phải (~0.45), phản ánh sự phân biệt tinh tế giữa vai trò người mua (buyer) và người bán (seller). Điều này cho thấy mô hình embedding không chỉ bắt các từ khóa chung chung mà còn phản ánh được mối quan hệ về mặt vai trò ngữ nghĩa trong không gian vector.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Mô hình Embedding sử dụng:** `LocalEmbedder` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) — Mô hình nhúng đa ngôn ngữ thực tế.

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src.K4-2A202601939-NguyenHoangSon` sử dụng các chiến lược chunking trên corpus `data/shopee_ecommerce/` (8 tài liệu chính sách công khai Shopee):

### Kết quả Benchmark theo Thang điểm Rubric (Chấm ở cấp độ Chunk):

| # | Câu hỏi (Query) | Metadata Filter | Top-1 Chunk truy xuất được (doc_id & score) | Đáp ứng Chuỗi đặc trưng đáp án? | Điểm Rubric (0/1/2) | Câu trả lời của Agent (tóm tắt) |
|---|-------|-----------------|---------------------------------------------|--------------------------------|----------------------|--------------------------------|
| 1 | Những lý do nào khiến Người mua có thể yêu cầu Trả hàng/Hoàn tiền? | None | `shopee-return-conditions` (`chunk_1`, score=0.6104) | Có (`trả hàng` xuất hiện trong Top-1) | **2 / 2** | Người mua có thể yêu cầu trả hàng/hoàn tiền khi chưa nhận được hàng, thiếu hàng, sai hàng hoặc hàng hư hỏng. |
| 2 | Người mua cần chuẩn bị và gửi bằng chứng trả hàng/hoàn tiền như thế nào? | None | `shopee-return-refund-policy` (`chunk_3`, score=0.6414) | Không ở Top-1 (chunk chứa `video` ở `shopee-return-request-process` nằm ngoài Top-3) | **0 / 2** | Agent trả về ngữ cảnh chung về xử lý hoàn tiền nhưng thiếu quy trình quay video mở kiện hàng cụ thể. |
| 3 | Khi nào Người mua không thể chọn COD và cần làm gì? | None | `shopee-cod-eligibility` (`chunk_1`, score=0.6968) | Có (`COD` & giải pháp chọn PTTT khác xuất hiện ở Top-1) | **2 / 2** | Nếu đơn hàng không đáp ứng điều kiện COD, Người mua phải chọn phương thức thanh toán khác. |
| 4 | Người bán phải mô tả sản phẩm như thế nào khi đăng bán? | `{"customer_role": "seller"}` | `shopee-seller-listing-policy` (`chunk_1`, score=0.6909) | Có (Chứa yêu cầu mô tả trung thực, rõ ràng) | **1 / 2** | Người bán phải mô tả đầy đủ, chi tiết, trung thực và rõ ràng đặc điểm, công dụng của sản phẩm. |
| 5 | Vi phạm chính sách hàng cấm/hạn chế có thể bị xử lý ra sao? | `{"customer_role": "seller"}` | `shopee-prohibited-products-policy` (`chunk_1`, score=0.5979) | Có (Chunk liệt kê các hình thức xử lý vi phạm) | **1 / 2** | Vi phạm có thể dẫn tới xóa sản phẩm, giới hạn quyền tài khoản, đình chỉ hoặc xóa tài khoản. |

**Tổng điểm Rubric Benchmark:** **6 / 10** điểm.

---

### Đánh giá Chi tiết: Chấm ở cấp độ Chunk (Chunk-Level vs Doc-ID Matching)

- **Tại sao chỉ kiểm tra `doc_id` là chưa đủ:** 
  Ở **Query 5**, nếu chỉ kiểm tra xem tài liệu `shopee-prohibited-products-policy` có xuất hiện trong Top-3 hay không, kết quả sẽ là 100% khớp (Match). Tuy nhiên, chấm ở cấp độ Chunk cho thấy: `chunk_index=1` (nói về nhóm hàng bị cấm) đứng Top-1 với score=0.5979, trong khi `chunk_index=2` (chứa câu trả lời trực tiếp về *Hậu quả xử lý vi phạm*) lại nhận score thấp hơn. Điều này chứng minh Cosine similarity đo độ tương đồng chủ đề chung chứ không đo độ tập trung câu trả lời.

---

### Đánh giá Thử nghiệm A/B Metadata Filter

Thử nghiệm so sánh khi **Có Filter (`customer_role="seller"`)** và **Không có Filter**:

- **Query 4 (Quy định mô tả sản phẩm cho Người bán):**
  - *Khi không dùng Filter:* Top-3 xuất hiện chunk từ `shopee-return-conditions` (Score = 0.6279) gây nhiễu từ chính sách Người mua.
  - *Khi áp dụng Filter `{"customer_role": "seller"}`:* Loại bỏ hoàn toàn 100% các tài liệu Người mua, 100% Top-3 chunks trả về đều thuộc `shopee-seller-listing-policy` và `shopee-prohibited-products-policy`. Score Top-1 đạt **0.6909**.
- **Kết luận:** Metadata Filter giúp tăng độ chính xác (Precision), loại bỏ nhiễu liên miền (cross-domain noise) giữa Người mua và Người bán.

---

### Phân tích Phân bố Lỗi (Failure Case Analysis)

- **Query thất bại rõ ràng nhất:** **Query 2** (*"Người mua cần chuẩn bị và gửi bằng chứng trả hàng/hoàn tiền như thế nào?"*)
- **Dấu hiệu thực nghiệm:**
  - `Top-1` Score = 0.6414: `shopee-return-refund-policy` (`chunk_3` — *"Người mua gửi yêu cầu; Người bán có thể phản hồi..."*)
  - `Top-2` Score = 0.6219: `shopee-cod-eligibility` (`chunk_1` — *"Nếu đơn hàng không đáp ứng điều kiện COD..."*)
  - `Top-3` Score = 0.6002: `shopee-return-request-process` (`chunk_5` — *"Sau khi chấp thuận, tiền hoàn..."*)
- **Nguyên nhân gốc rễ (Root Cause):**
  1. Chunk chứa từ khóa quan trọng `"quay video mở kiện hàng"` nằm ở `shopee-return-request-process` (`chunk_2`), nhưng câu hỏi sử dụng cụm từ *"bằng chứng trả hàng"*. Vector nhúng ngữ nghĩa (`paraphrase-multilingual-MiniLM-L12-v2`) ưu tiên tài liệu tổng quan chính sách (`shopee-return-refund-policy`) hơn là tài liệu quy trình thao tác chi tiết.
  2. Cosine similarity đánh giá điểm dựa trên bối cảnh chung của tài liệu chính sách hoàn tiền chứ không nhận diện được mật độ thông tin quy trình thao tác (procedural density).
- **Giải pháp đề xuất (Actionable Proposal):**
  1. **Bổ sung Metadata Section / Heading:** Gắn metadata `section_title: "gửi bằng chứng"` vào từng chunk để có thể filter hoặc rerank.
  2. **Tìm kiếm lai (Hybrid Search):** Kết hợp BM25 (tìm kiếm từ khóa chính xác như `video`, `bằng chứng`) với Dense Vector Search để đảm bảo các chunk chứa từ khóa thao tác cụ thể không bị đẩy khỏi Top-3.




---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
