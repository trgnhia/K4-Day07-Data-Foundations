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

### Cấu hình chạy

- **Corpus:** `data/shopee_ecommerce/` — 8 tài liệu chính sách công khai của Shopee.
- **Embedder:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (local, 384 chiều).
- **Chiến lược cá nhân:** `HeadingSectionChunker(chunk_size=650)` — giữ tiêu đề Markdown cấp 1 cùng từng section/điều khoản; 8 tài liệu tạo 23 chunks và không có chunk chỉ chứa heading.
- **top_k:** 3.
- **Agent:** dùng extractive demo LLM, chỉ trả lại ngữ cảnh đã retrieve; phần “câu trả lời” dưới đây là tóm tắt có căn cứ từ context đó, không thêm thông tin ngoài corpus.

| # | Câu hỏi (Query) | Top-3 chunks (`doc_id: score`) | Top-1 | Có liên quan trong top-3? | Câu trả lời agent có căn cứ (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Những lý do nào khiến Người mua có thể yêu cầu Trả hàng hoặc Hoàn tiền? | `shopee-return-refund-policy: 0.642`; `shopee-return-refund-policy: 0.632`; `shopee-return-conditions: 0.600` | `shopee-return-refund-policy: 0.642` | Có | Các lý do gồm chưa nhận/thiếu/sai hàng, hư hỏng, lỗi, khác mô tả, hàng cũ, giả hoặc nhái. |
| 2 | Người mua cần chuẩn bị và gửi bằng chứng trả hàng hoặc hoàn tiền như thế nào? | `shopee-return-refund-policy: 0.632`; `shopee-return-refund-policy: 0.629`; `shopee-return-request-process: 0.610` | `shopee-return-refund-policy: 0.632` | Có | Chuẩn bị video mở kiện liên tục, ảnh sản phẩm/tem nhãn/kiện hàng; trong đơn chọn Trả hàng/Hoàn tiền, lý do, mô tả và tải bằng chứng. |
| 3 | Khi nào Người mua không thể chọn COD và cần làm gì? | `shopee-cod-eligibility: 0.622`; `shopee-return-conditions: 0.562`; `shopee-seller-listing-policy: 0.555` | `shopee-cod-eligibility: 0.622` | Có | COD chỉ dùng cho đơn/khu vực đủ điều kiện; nếu không đủ điều kiện thì chọn phương thức thanh toán khác. |
| 4 | Người bán phải mô tả sản phẩm như thế nào khi đăng bán? `customer_role=seller` | `shopee-seller-listing-policy: 0.743`; `shopee-seller-listing-policy: 0.670`; `shopee-prohibited-products-policy: 0.469` | `shopee-seller-listing-policy: 0.743` | Có | Mô tả phải đầy đủ, chi tiết, trung thực, rõ ràng; nêu thông tin sản phẩm cần thiết và không chứa thông tin liên hệ để quảng cáo/dẫn web khác. |
| 5 | Vi phạm chính sách hàng cấm/hạn chế có thể bị xử lý ra sao? `customer_role=seller` | `shopee-prohibited-products-policy: 0.647`; `shopee-prohibited-products-policy: 0.633`; `shopee-prohibited-products-policy: 0.592` | `shopee-prohibited-products-policy: 0.647` | Có | Có thể bị xóa sản phẩm, hạn chế/đình chỉ/xóa tài khoản, cấn trừ số dư hoặc phong tỏa quyền rút tiền, cùng các biện pháp theo chính sách/pháp luật. |

**Kết quả:** **5 / 5** query có chunk liên quan trong top-3.

### Nhận xét và failure analysis

Query 2 có chunk chứa quy trình/bằng chứng ở hạng 3, trong khi hai chunk đầu thuộc chính sách tổng quát. Đây là failure case nhẹ: kết quả vẫn có đủ trong top-3, nhưng agent cần đọc đủ ba chunk để trả lời cụ thể. Có thể cải thiện bằng cách giảm `chunk_size` cho tài liệu quy trình, thêm metadata `section=proof`/`section=steps`, hoặc dùng reranking sau retrieval.

Filter `customer_role=seller` giúp query 4 và 5 chỉ xét hai chính sách dành cho người bán, loại nhiễu từ đổi trả/thanh toán dành cho người mua.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code (42/42 tests) | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất của tôi | 10 / 10 |
| **Tổng phần cá nhân hiện có thể xác minh** | **60 / 60** |
