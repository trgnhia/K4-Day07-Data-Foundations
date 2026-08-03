# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Đại Nghĩa  
**MSSV:** 2A202601328  
**Nhóm:** Chưa cập nhật  
**Ngày:** 03/08/2026

## 1. Khởi động (Warm-up)

### Độ tương tự cosine

Độ tương tự cosine cao nghĩa là hai embedding có hướng gần nhau; với một embedder ngữ nghĩa tốt, điều đó thường cho thấy hai đoạn văn nói về ý tưởng tương tự. Cosine đo hướng thay vì độ dài vector, nên hai đoạn có độ dài khác nhau vẫn có thể được nhận diện là liên quan.

**Ví dụ có độ tương tự cao:**

- Câu A: “Người mua có thể yêu cầu trả hàng khi sản phẩm bị lỗi.”
- Câu B: “Khách hàng được gửi yêu cầu đổi trả nếu hàng không đúng mô tả.”
- Cả hai đều nói về quyền đổi trả của người mua khi sản phẩm có vấn đề.

**Ví dụ có độ tương tự thấp:**

- Câu A: “Chính sách đổi trả yêu cầu bằng chứng về lỗi sản phẩm.”
- Câu B: “Hôm nay trời mưa lớn ở Hà Nội.”
- Hai câu thuộc hai chủ đề không liên quan: chính sách TMĐT và thời tiết.

Cosine similarity phù hợp cho text embedding vì norm của embedding có thể bị ảnh hưởng bởi độ dài hoặc đặc trưng kỹ thuật của mô hình. Điều quan trọng trong retrieval là hướng/quan hệ ngữ nghĩa của vector, không phải khoảng cách tuyệt đối giữa các tọa độ như Euclidean distance.

### Bài toán chunking

Với tài liệu dài 10.000 ký tự, `chunk_size=500`, `overlap=50`:

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks`.

Nếu `overlap=100`, số chunk là `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks`. Overlap lớn hơn làm tăng số chunk và chi phí embedding/lưu trữ, nhưng giữ lại ngữ cảnh nằm ở ranh giới chunk nên giảm nguy cơ cắt mất một ý quan trọng.

## 2. Hướng tiếp cận của tôi

### Các hàm chunking

`SentenceChunker.chunk` dùng regex `(?<=[.!?])\s+` để tách sau dấu kết thúc câu, bỏ phần tử rỗng và ghép tối đa `max_sentences_per_chunk` câu vào một chunk. Hàm trả về danh sách rỗng với input rỗng hoặc chỉ chứa khoảng trắng.

`RecursiveChunker` ưu tiên lần lượt `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là cắt theo ký tự. Thuật toán ghép các phần nhỏ đến khi chạm `chunk_size`; phần vượt giới hạn được tách đệ quy bằng separator có ưu tiên thấp hơn. Base case là đoạn đã đủ ngắn hoặc không còn separator để sử dụng.

### EmbeddingStore

Mỗi `Document` được chuyển thành record gồm `id`, `content`, `metadata` và `embedding`; `doc_id` được bổ sung vào metadata khi thiếu. `search` nhúng query, tính dot product với mọi embedding, sắp xếp giảm dần theo score và trả tối đa `top_k` kết quả.

`search_with_filter` lọc metadata trước rồi mới xếp hạng vector, để kết quả không vi phạm điều kiện như `customer_role=seller`. `delete_document` tạo lại danh sách record, loại tất cả record có `metadata['doc_id']` trùng giá trị cần xóa và trả về trạng thái đã xóa hay chưa.

### KnowledgeBaseAgent

`answer` lấy top-k chunks từ store, đánh số từng nguồn và ghép thành phần **Ngữ cảnh** của prompt. Prompt yêu cầu LLM chỉ trả lời dựa trên ngữ cảnh và nói rõ khi thiếu thông tin; sau đó agent chuyển prompt cho `llm_fn`.

## 3. Hoàn thiện code

Mã nguồn cá nhân nằm trong thư mục `src/K4_2A202601328_Trần Đại Nghĩa/` gồm `chunking.py`, `store.py`, `agent.py`, `models.py` và `__init__.py`.

Kết quả kiểm thử:

```text
Ran 42 tests in 0.011s

OK
```

**Số lượng bài test vượt qua:** **42 / 42**

Lệnh đã dùng trên PowerShell:

```powershell
$env:LAB_SOLUTION_PACKAGE='src.K4_2A202601328_Trần Đại Nghĩa'
python -m unittest discover -s tests -v
Remove-Item Env:LAB_SOLUTION_PACKAGE
```

## 4. Dự đoán độ tương tự

Các điểm dưới đây dùng `MockEmbedder` của bài lab để kiểm tra hàm `compute_similarity`. Mock embedder là deterministic nhưng không biểu diễn ngữ nghĩa thật; vì vậy bảng này chủ yếu xác minh công thức cosine, không dùng để kết luận chất lượng retrieval tiếng Việt.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Chính sách đổi trả cho phép người mua gửi yêu cầu khi hàng lỗi. | Người mua có thể yêu cầu trả hàng nếu sản phẩm không đúng mô tả. | cao | 0.0583 | Không |
| 2 | Người bán phải cung cấp giá và mô tả sản phẩm chính xác. | Người bán cần đăng thông tin hàng hóa trung thực. | cao | 0.1690 | Có (cao hơn cặp 1) |
| 3 | Tôi muốn đổi trả sản phẩm bị lỗi. | Hôm nay trời mưa lớn ở Hà Nội. | thấp | -0.0405 | Có |
| 4 | Vector store dùng embedding để tìm văn bản liên quan. | Cơ sở dữ liệu vector hỗ trợ tìm kiếm tương đồng ngữ nghĩa. | cao | 0.4143 | Có |
| 5 | Khách hàng cần bằng chứng khi yêu cầu đổi trả. | Sản phẩm bị cấm không được phép đăng bán. | thấp | -0.2085 | Có |

Kết quả bất ngờ nhất là cặp 1 có nội dung gần nhau nhưng score rất thấp. Lý do là mock embedding sinh vector từ hash của toàn bộ chuỗi, không được huấn luyện để đưa câu đồng nghĩa về gần nhau. Khi đánh giá retrieval thực tế, cần dùng `EMBEDDING_PROVIDER=local` với multilingual embedder thay vì mock.

## 5. Kết quả truy xuất của tôi

Phần này phụ thuộc vào **đúng 5 benchmark queries chung** và corpus 5–10 tài liệu công khai do nhóm thống nhất. Tại thời điểm viết báo cáo, repo chỉ có 2 tài liệu khởi động với URL `example.com`, nên chúng không đủ điều kiện làm corpus chính thức và không thể ghi kết quả benchmark như kết quả nộp cuối.

Kế hoạch chạy lại ngay khi nhóm chốt corpus:

1. Cài `requirements-local.txt`, đặt `EMBEDDING_PROVIDER=local`.
2. Dùng chung 5 query/gold answer của `REPORT_NHOM.md`.
3. Nạp corpus bằng `build_knowledge_base(...)`, chạy `search(..., top_k=3)` hoặc `search_with_filter(...)` cho câu hỏi theo vai trò buyer/seller.
4. Ghi top-1, score, mức liên quan và tóm tắt câu trả lời agent vào bảng bên dưới.

| # | Câu hỏi (Query chung của nhóm) | Top-1 chunk | Score | Relevant | Câu trả lời Agent |
|---|---|---|---:|---|---|
| 1 | Chờ nhóm chốt | Chờ chạy benchmark | — | — | — |
| 2 | Chờ nhóm chốt | Chờ chạy benchmark | — | — | — |
| 3 | Chờ nhóm chốt | Chờ chạy benchmark | — | — | — |
| 4 | Chờ nhóm chốt | Chờ chạy benchmark | — | — | — |
| 5 | Chờ nhóm chốt; có ít nhất một metadata filter buyer/seller | Chờ chạy benchmark | — | — | — |

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code (42/42 tests) | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất của tôi | Chờ benchmark nhóm / 10 |
| **Tổng phần cá nhân hiện có thể xác minh** | **50 / 60** |
