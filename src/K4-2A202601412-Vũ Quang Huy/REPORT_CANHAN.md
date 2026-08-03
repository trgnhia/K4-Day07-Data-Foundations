# Báo cáo cá nhân – Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Quang Huy  
**Mã sinh viên:** K4-2A202601412  
**Ngày:** 03/08/2026

---

# 1. Khởi động (Warm-up) – Cá nhân

## Bài tập 1.1 – Cosine Similarity

### Cosine similarity cao nghĩa là gì?

Khi hai đoạn văn bản có **cosine similarity cao**, các vector embedding của chúng có hướng gần giống nhau. Điều này thường cho thấy hai văn bản có nội dung, chủ đề hoặc ý nghĩa tương đồng, ngay cả khi cách diễn đạt hoặc từ ngữ sử dụng khác nhau.

### Ví dụ có độ tương tự cao

**Câu A:** Khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày nếu hàng bị lỗi.

**Câu B:** Nếu sản phẩm gặp lỗi, người mua được yêu cầu hoàn trả trong thời hạn một tuần.

**Giải thích:**

Hai câu đều diễn đạt cùng một ý: người mua được phép trả lại sản phẩm bị lỗi trong khoảng thời gian 7 ngày, chỉ khác cách diễn đạt.

### Ví dụ có độ tương tự thấp

**Câu A:** Hệ thống hỗ trợ thanh toán bằng thẻ ngân hàng.

**Câu B:** Công thức nấu phở bò cần nước dùng trong và thơm.

**Giải thích:**

Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau (thương mại điện tử và nấu ăn), nên có mức độ tương đồng rất thấp.

### Vì sao Cosine Similarity được ưu tiên hơn khoảng cách Euclidean?

Cosine Similarity chỉ quan tâm đến **hướng của vector**, nên phù hợp để so sánh mức độ giống nhau về ngữ nghĩa giữa các văn bản. Trong khi đó, khoảng cách Euclidean chịu ảnh hưởng bởi độ lớn của vector, điều không quá quan trọng đối với bài toán biểu diễn văn bản bằng embedding.

---

## Bài tập 1.2 – Tính toán Chunking

Với tài liệu có **10.000 ký tự**, `chunk_size = 500`, `overlap = 50`

```text
Số chunk = ceil((10000 - 50) / (500 - 50))
          = ceil(9950 / 450)
          = ceil(22.11)
          = 23 chunk
```

### Nếu tăng overlap lên 100

```text
Số chunk = ceil((10000 - 100) / (500 - 100))
          = ceil(9900 / 400)
          = ceil(24.75)
          = 25 chunk
```

Khi tăng overlap từ **50** lên **100**, số lượng chunk tăng từ **23** lên **25** do khoảng trượt giữa hai chunk nhỏ hơn. Tuy nhiên, overlap lớn giúp giữ được nhiều ngữ cảnh hơn ở ranh giới giữa các chunk, từ đó cải thiện chất lượng truy xuất thông tin.

---

# 2. Hướng tiếp cận của tôi

## `SentenceChunker.chunk`

Tôi sử dụng biểu thức chính quy `(?<=[.!?])\s+` để tách văn bản tại khoảng trắng nằm sau dấu kết thúc câu. Sau khi tách, các câu rỗng sẽ được loại bỏ và các câu còn lại được gom thành từng nhóm với số lượng tối đa là `max_sentences_per_chunk`. Nếu văn bản đầu vào rỗng, hàm sẽ trả về danh sách rỗng.

## `RecursiveChunker.chunk` và `_split`

Tôi triển khai thuật toán chia văn bản theo hướng đệ quy với thứ tự ưu tiên các separator như sau:

- Đoạn văn (`\n\n`)
- Dòng (`\n`)
- Câu
- Từ
- Cuối cùng là cắt cố định theo kích thước (`Fixed Size`)

Điều kiện dừng của đệ quy là khi đoạn văn bản đã nhỏ hơn `chunk_size` hoặc không còn separator phù hợp. Nếu một đoạn vẫn quá dài thì hàm tiếp tục chia bằng separator ở mức ưu tiên thấp hơn.

## `compute_similarity`

Hàm được xây dựng theo công thức Cosine Similarity:

\[
\frac{A \cdot B}{||A|| \times ||B||}
\]

Nếu một trong hai vector có độ dài bằng 0 thì hàm trả về `0.0` để tránh lỗi chia cho 0.

## `ChunkingStrategyComparator`

Lớp này chạy đồng thời ba chiến lược:

- FixedSizeChunker
- SentenceChunker
- RecursiveChunker

Sau đó thống kê:

- Số lượng chunk
- Độ dài trung bình
- Độ dài nhỏ nhất
- Độ dài lớn nhất
- Danh sách các chunk

để dễ dàng so sánh hiệu quả của từng chiến lược.

## `EmbeddingStore`

Tôi sử dụng bộ nhớ trong (in-memory) để lưu trữ embedding nhằm giúp việc kiểm thử diễn ra nhanh và không phụ thuộc vào ChromaDB.

Mỗi document được lưu gồm:

- `id`
- `content`
- `metadata`
- `embedding`

Khi tìm kiếm, câu truy vấn sẽ được embedding trước, sau đó tính độ tương đồng với từng document trong store, sắp xếp theo điểm similarity giảm dần và trả về `top_k` kết quả.

## `search_with_filter` và `delete_document`

Đối với `search_with_filter`, tôi thực hiện lọc theo metadata trước, sau đó mới tiến hành tính độ tương đồng trên tập tài liệu đã được lọc.

Đối với `delete_document`, hệ thống sẽ xóa toàn bộ document có `id` hoặc `metadata["doc_id"]` trùng với giá trị được yêu cầu.

## `KnowledgeBaseAgent.answer`

Agent sẽ thực hiện truy xuất các chunk liên quan nhất từ `EmbeddingStore`, sau đó ghép các chunk này thành phần **Context** trong prompt.

Prompt yêu cầu mô hình chỉ trả lời dựa trên ngữ cảnh được cung cấp. Nếu thông tin trong context không đủ để trả lời thì cần thông báo rõ thay vì tự suy diễn.

---

# 3. Hoàn thiện Code – Kết quả kiểm thử

### Lệnh thực hiện

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ -v
```

### Kết quả

```text
collected 42 items

42 passed in 0.19s
```

**Số lượng bài kiểm thử vượt qua:** **42 / 42**

---

# 4. Dự đoán độ tương tự

Do bài lab sử dụng `_mock_embed` để sinh embedding nên điểm similarity chỉ mang tính mô phỏng và không phản ánh chính xác khả năng hiểu ngữ nghĩa như các mô hình embedding thực tế.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|--------|--------|----------|-------------:|:-----:|
| 1 | Đổi trả hàng trong 7 ngày | Khách có thể hoàn hàng trong vòng 7 ngày | Cao | 0.2226 | ✅ |
| 2 | Phí vận chuyển được tính theo khu vực | Cước giao hàng phụ thuộc địa chỉ nhận | Cao | 0.0274 | Gần đúng |
| 3 | Người bán phải cung cấp thông tin sản phẩm chính xác | Mô tả sản phẩm cần đúng sự thật | Cao | -0.0647 | ❌ |
| 4 | Chính sách bảo mật dữ liệu cá nhân | Công thức nấu phở bò truyền thống | Thấp | -0.1008 | ✅ |
| 5 | Thanh toán bằng thẻ ngân hàng | Thời tiết hôm nay có mưa không | Thấp | -0.2119 | ✅ |

### Kết quả bất ngờ nhất

Cặp số 3 có nội dung gần như cùng ý nghĩa nhưng điểm similarity lại âm. Điều này cho thấy `_mock_embed` chỉ tạo embedding giả lập phục vụ kiểm thử nên không thực sự hiểu ngữ nghĩa của văn bản. Vì vậy, nó phù hợp cho unit test nhưng không phản ánh chất lượng retrieval trong thực tế.

---

# 5. Kết quả truy xuất của tôi (Benchmark 5 Queries – RecursiveChunker 400)

Tôi sử dụng **RecursiveChunker** với `chunk_size = 400` trên corpus `data/shopee_ecommerce` (gồm 8 file chính sách Shopee, tạo ra tổng cộng **28 chunks**). 

> **Ghi chú về Embedder:** Do môi trường Windows có chính sách AppLocker ngăn nạp DLL/C-extension (`_regex.pyd`/`_xxhash.pyd`), bài thử nghiệm sử dụng `MockEmbedder` (deterministic hash). Vì vậy, kết quả benchmark tập trung đánh giá số chunk, độ mạch lạc (chunk coherence), tính truy vết (provenance) và hiệu quả của metadata filter.

### Bảng kết quả 5 Query Benchmark

| # | Câu hỏi (Query) | Top-1 Chunk | Score | Top-3 có đáp án? | A/B Metadata Filter | Câu trả lời Agent |
|---|----------|-------------|------:|:---------:|-------------------|-------------------|
| 1 | Những lý do nào khiến người mua có thể yêu cầu Trả hàng/Hoàn tiền? | `shopee-cod-eligibility::chunk_1` | 0.2149 | Có (ở Top-3: `shopee-return-conditions::chunk_2`) | Không dùng | Trả lời dựa trên context được cung cấp |
| 2 | Người mua cần chuẩn bị bằng chứng như thế nào? | `shopee-return-refund-policy::chunk_1` | 0.2525 | Có (Top-1 & Top-2) | Không dùng | Trả lời dựa trên context được cung cấp |
| 3 | Khi nào người mua không thể chọn COD? | `shopee-cod-eligibility::chunk_0` | 0.2630 | Có (Top-1) | Không dùng | Trả lời dựa trên context được cung cấp |
| 4 | Người bán phải mô tả sản phẩm như thế nào khi đăng bán? | `shopee-seller-listing-policy::chunk_3` | 0.1580 | Có (Top-1) | `customer_role = seller` | Trả lời dựa trên context được cung cấp |
| 5 | Vi phạm chính sách hàng cấm sẽ bị xử lý ra sao? | `shopee-prohibited-products-policy::chunk_0` | 0.2469 | Có (Top-1 & Top-2) | `customer_role = seller` | Trả lời dựa trên context được cung cấp |

---

## Đánh giá chi tiết (Phân tích theo tiêu chí Checkpoint 6)

1. **Precision ở mức Chunk (Chunk-level Precision):**
   - **Tỷ lệ Top-3 chứa chunk có đáp án:** **5 / 5 query (100%)**.
   - **Tỷ lệ Top-1 chứa chunk có đáp án:** **4 / 5 query (80%)**.

2. **Hiệu quả của Metadata Filter (A/B Testing):**
   - Khi chạy **không có filter** cho Query 4 & 5: Các chunk dành cho buyer (đổi trả, thanh toán COD) dễ chen vào Top-3 do chứa các từ khóa chung như "Người mua", "Shopee".
   - Khi áp dụng `metadata_filter = {"customer_role": "seller"}`: Tập ứng viên giảm từ **28 chunks xuống còn 8 chunks**, loại bỏ 100% các tài liệu rác dành riêng cho buyer. Nhờ đó, Top-1 và Top-2 lập tức thu hẹp chính xác vào `shopee-seller-listing-policy` và `shopee-prohibited-products-policy`.

3. **Độ mạch lạc (Chunk Coherence & Provenance):**
   - `RecursiveChunker(chunk_size=400)` cắt ưu tiên theo đoạn `\n\n` và câu `. `, giúp giữ nguyên câu và cấu trúc ý nghĩa, không bị ngắt rủn giữa từ như `FixedSizeChunker`.
   - Các chunk được gán định danh `doc_id::chunk_index` giúp `KnowledgeBaseAgent` dẫn nguồn minh bạch (grounding), trỏ ngược về đúng tài liệu gốc trong `sources.csv`.

---

## Phân tích trường hợp truy xuất chưa tốt (Failure Case Analysis)

### Query
> *Những lý do nào khiến người mua có thể yêu cầu Trả hàng/Hoàn tiền?*

### Bằng chứng kết quả Top-3 nhận được:
1. **Top-1 (`score = 0.2149`):** `shopee-cod-eligibility::chunk_1` — *"Nếu đơn hàng không đáp ứng điều kiện COD, Người mua phải chọn phương thức thanh toán khác..."* (Nhiễu, không chứa lý do đổi trả).
2. **Top-2 (`score = 0.1977`):** `shopee-shipping-policy::chunk_0` — *"Chính sách vận chuyển Shopee..."* (Nhiễu).
3. **Top-3 (`score = 0.1827`):** `shopee-return-conditions::chunk_2` — *"Một số người mua thuộc nhóm Thành viên Kim Cương... có thể được trả hàng vì đổi ý nếu sản phẩm chưa sử dụng..."* (Chứa đúng đáp án nhưng bị tụt xuống Top-3).

### Nguyên nhân thất bại:
1. **Đặc điểm Cosine Similarity với Mock Embedder:** Mock embedder tính điểm dựa trên băm chuỗi văn bản (hash), dẫn đến các từ khóa xuất hiện nhiều lần như *"Người mua"*, *"Shopee"*, *"hoàn tiền"* ở bài viết COD bị chấm điểm cao hơn chunk chứa nội dung liệt kê chi tiết. Cosine similarity đo độ giống chủ đề chung chứ không đo độ đậm đặc thông tin đáp án.
2. **Ranh giới Recursive Chunking:** `RecursiveChunker` cắt theo ranh giới `\n\n`. File `shopee-return-conditions.md` có tiêu đề `## Các lý do có thể được chấp nhận` bị tách riêng thành 1 chunk nhỏ, trong khi danh sách lý do liệt kê bên dưới bị đẩy sang chunk tiếp theo, làm phân tán tín hiệu từ khóa.

### Đề xuất cải thiện:
1. **Bổ sung Separator Markdown Heading:** Thêm `\n# `, `\n## ` vào `DEFAULT_SEPARATORS` của `RecursiveChunker` để gộp tiêu đề mục cùng với toàn bộ danh sách liệt kê bên dưới trong một chunk.
2. **Áp dụng Pre-filtering theo Category:** Đưa thêm `metadata_filter = {"category": "return-conditions"}` hoặc `{"customer_role": "buyer"}` để thu hẹp không gian tìm kiếm trước khi tính score similarity.
3. **Sử dụng Semantic Embedding Model:** Chuyển sang mô hình nhúng đa ngôn ngữ thực sự như `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` để bắt chính xác quan hệ ngữ nghĩa thay vì phụ thuộc tần suất từ khóa.

---

# Tự đánh giá

| Tiêu chí | Điểm |
|----------|------:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất & Phân tích Failure | 10 / 10 |
| **Tổng điểm** | **60 / 60** |