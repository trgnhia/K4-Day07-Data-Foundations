# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đức Mạnh
**Nhóm:** NoName
**Mã HV:** 2A202601176
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai đoạn văn bản có nhiều từ/ngữ mang ý nghĩa gần nhau, vector embeddings của chúng hướng về cùng phía trong không gian vector, nên cosine similarity cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Python is a programming language."
- Câu B: "Python is a language used for programming."
- Tại sao tương đồng: Cả hai nói về cùng một ý tưởng với từ ngữ gần giống.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Python is a programming language."
- Câu B: "The cat sat on the mat."
- Tại sao khác: Nội dung và ngữ cảnh hoàn toàn khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì embeddings thường có nhiều chiều và độ lớn tổng quát không quá quan trọng; cosine nhấn vào hướng của vector, tức là ý nghĩa, hơn là khoảng cách tuyệt đối.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunks sẽ giảm vì bước dịch chuyển tăng từ 450 lên 400. Độ chồng chéo lớn giúp giữ ngữ cảnh liên tục giữa các chunk, nhưng tăng chi phí dư thừa và làm giảm số lượng chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex để tách theo các ranh giới câu như ". ", "! ", "? ". Sau đó nhóm các câu thành từng chunk theo số câu tối đa. Nếu đầu vào rỗng hoặc chỉ có khoảng trắng thì trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt các separator theo ưu tiên, nếu một đoạn văn bản có thể được chia thành nhiều phần thì đệ quy tiếp trên từng phần; khi không còn separator phù hợp hoặc vượt quá kích thước, dùng fallback theo kích thước cố định.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được chuyển thành record có nội dung, metadata và embedding. Quá trình tìm kiếm tính similarity giữa query embedding và embedding của từng record rồi sắp xếp giảm dần theo score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi thực hiện lọc metadata trước khi tính similarity để giới hạn không gian tìm kiếm. Xóa document bằng cách giữ lại các record không thuộc doc_id cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunks liên quan, nối chúng thành ngữ cảnh rồi chèn vào prompt. Prompt này được truyền cho hàm LLM để trả lời ngắn gọn và có căn cứ vào ngữ cảnh.

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
> Điều đáng chú ý là các câu có cùng ý tưởng nhưng khác từ ngữ vẫn có cosine similarity khá cao. Điều này cho thấy embeddings không chỉ dựa vào từ khớp chính xác mà còn nắm được ý nghĩa tổng quát.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Chính sách đổi trả như thế nào? | Thông tin về điều kiện đổi trả và thời hạn | cao | Có | Trả lời ngắn gọn dựa trên chunk liên quan |
| 2 | Quyền riêng tư của người dùng là gì? | Nội dung chính sách bảo mật | cao | Có | Tóm tắt đúng mục tiêu chính sách |
| 3 | Phương thức thanh toán được hỗ trợ? | Các phương thức thanh toán và điều kiện | cao | Có | Kể các phương thức chính |
| 4 | Điều kiện người bán như thế nào? | Các yêu cầu về hồ sơ và tuân thủ | cao | Có | Tóm tắt chính sách người bán |
| 5 | Giao hàng có thể mất bao lâu? | Thông tin thời gian giao hàng và phát sinh | cao | Có | Cung cấp thông tin tổng quát |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc dùng metadata filter giúp tìm kiếm ngắn gọn và đúng trọng tâm hơn. Chunking phù hợp với cấu trúc tài liệu và độ dài câu cũng ảnh hưởng lớn đến chất lượng retrieval.

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
