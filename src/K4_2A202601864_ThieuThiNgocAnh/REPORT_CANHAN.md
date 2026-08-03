# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Thiều Thị Ngọc Ánh
**Nhóm:** K4
**Ngày:** 03/08/2026


## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai đoạn văn bản có nhiều từ/ngữ mang ý nghĩa gần nhau, vector embeddings của chúng hướng về cùng phía trong không gian vector, nên cosine similarity cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Python is a programming language."
- Câu B: "Python is a language used for programming."
- Tại sao tương đồng: Cả hai câu đều truyền tải cùng ý tưởng với cấu trúc ngôn ngữ tương tự.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Python is a programming language."
- Câu B: "The cat sat on the mat."
- Tại sao khác: Nội dung và ngữ cảnh hoàn toàn khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì embeddings thường có nhiều chiều và độ lớn vector không quan trọng bằng hướng. Cosine similarity đo mức độ đồng hướng giữa hai vector, nên tập trung vào ý nghĩa hơn là khoảng cách tuyệt đối.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunks giảm vì bước dịch chuyển từ 450 xuống 400. Độ chồng chéo lớn giữ ngữ cảnh liên tục hơn giữa các chunk, nhưng cũng tạo ra nhiều phần trùng lặp và tăng chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex để tách theo các câu cuối như `.`, `?`, `!`, sau đó gom các câu lại thành chunk theo số ký tự hoặc số câu tối đa. Nếu văn bản quá dài, dùng chiến lược chia đệ quy.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử chia theo các separator ưu tiên, nếu vẫn còn quá dài thì chia nhỏ hơn cho tới khi được chunk hợp lý.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được chuyển thành record chứa nội dung, metadata và embedding. Khi tìm kiếm, tôi tính tương đồng cosine giữa query và từng record, sau đó sắp xếp giảm dần theo score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Với lọc metadata, tôi giới hạn tập candidate trước khi tính similarity. Xóa document được thực hiện bằng cách loại bỏ record có `doc_id` tương ứng.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunks có score cao nhất, nối chúng thành ngữ cảnh rồi tạo prompt cho LLM để trả lời ngắn gọn, có dẫn chứng từ nguồn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```
============================= 42 passed in 0.17s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python là ngôn ngữ lập trình | Python là ngôn ngữ lập trình | cao | cao | Có |
| 2 | Tôi thích ăn phở | Tôi thích uống cà phê | thấp | thấp | Có |
| 3 | Mạng neural sâu học từ dữ liệu | Học máy dùng dữ liệu để học | cao | cao | Có |
| 4 | Con mèo ngủ trên ghế | Trái đất quay quanh mặt trời | thấp | thấp | Có |
| 5 | Vector store lưu embeddings | CSDL vector lưu embedding để tìm kiếm tương đồng | cao | cao | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Các câu có cùng chủ đề nhưng khác từ ngữ vẫn có điểm tương đồng cao. Điều đó cho thấy embeddings đại diện ý nghĩa tốt hơn chỉ khớp chuỗi ký tự.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src`. **Các câu hỏi này trùng với nhóm**.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Ghi chú |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Shopee quy định như thế nào về hoàn tiền? | Điều kiện hoàn tiền và quy định trả hàng | cao | Có | Chunk trích nội dung chính sách refund |
| 2 | Điều kiện Shopee từ chối yêu cầu trả hàng? | Mô tả điều kiện từ chối trả hàng | cao | Có | Chunk liên quan rõ ràng |
| 3 | Tiêu chuẩn đăng bán sản phẩm trên Shopee? | Yêu cầu về nội dung và danh mục sản phẩm | cao | Có | Chunk phù hợp với câu hỏi |
| 4 | Seller phải làm gì khi khách yêu cầu đổi trả? | Hướng dẫn trả hàng/đổi trả cho seller | cao | Có | Chunk nêu rõ trách nhiệm seller |
| 5 | Seller cần chuẩn bị gì để giao hàng thành công? | Điều kiện giao hàng và chuẩn bị hồ sơ | cao | Có | Chunk chứa thông tin giao hàng |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều tôi học được từ nhóm: **
> Việc dùng metadata filter giúp tập trung vào nhóm tài liệu phù hợp hơn. Chunking đúng độ dài giữ ngữ cảnh tốt và nâng cao chất lượng truy xuất.

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
