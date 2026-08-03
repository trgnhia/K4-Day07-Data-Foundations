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

# 5. Kết quả truy xuất của tôi

Tôi sử dụng **RecursiveChunker** với `chunk_size = 400` để chạy 5 câu hỏi benchmark trên tập dữ liệu `data/shopee_ecommerce`.

| # | Câu hỏi | Top-1 Chunk | Score | Liên quan | Câu trả lời Agent |
|---|----------|-------------|------:|:---------:|-------------------|
| 1 | Những lý do nào khiến người mua có thể yêu cầu Trả hàng/Hoàn tiền? | `shopee-cod-eligibility::chunk_1` | 0.2149 | ❌ | Trả lời dựa trên context |
| 2 | Người mua cần chuẩn bị bằng chứng như thế nào? | `shopee-return-refund-policy::chunk_1` | 0.2525 | ✅ | Trả lời dựa trên context |
| 3 | Khi nào người mua không thể chọn COD? | `shopee-cod-eligibility::chunk_0` | 0.2630 | ✅ | Trả lời dựa trên context |
| 4 | Người bán phải mô tả sản phẩm như thế nào? *(customer_role = seller)* | `shopee-seller-listing-policy::chunk_3` | 0.1580 | ✅ | Trả lời dựa trên context |
| 5 | Vi phạm chính sách hàng cấm sẽ bị xử lý ra sao? *(customer_role = seller)* | `shopee-prohibited-products-policy::chunk_0` | 0.2469 | ✅ | Trả lời dựa trên context |

**Số câu truy xuất đúng trong Top-3:** **4 / 5**

---

## Phân tích trường hợp truy xuất chưa tốt

### Query

> Những lý do nào khiến người mua có thể yêu cầu Trả hàng/Hoàn tiền?

### Kết quả Top-3

1. `shopee-cod-eligibility::chunk_1`
2. `shopee-shipping-policy::chunk_0`
3. `shopee-return-conditions::chunk_2` *(chứa đúng nội dung cần tìm)*

### Nguyên nhân

- `RecursiveChunker` chia tài liệu theo ranh giới đoạn hoặc dòng nên phần tiêu đề và danh sách lý do bị tách thành nhiều chunk khác nhau.
- `_mock_embed` không hiểu ngữ nghĩa nên các từ khóa phổ biến như "Shopee", "người mua", "hoàn tiền" có thể làm sai lệch kết quả truy xuất.

### Hướng cải thiện

- Bổ sung separator theo Markdown Heading (`#`, `##`) để giữ nguyên nội dung của từng mục.
- Áp dụng thêm `metadata filter` theo `category` hoặc `customer_role`.
- Thay `_mock_embed` bằng mô hình embedding thực như `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` để đánh giá chính xác hơn.

---

# Tự đánh giá

| Tiêu chí | Điểm |
|----------|------:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất | 10 / 10 |
| **Tổng điểm** | **60 / 60** |