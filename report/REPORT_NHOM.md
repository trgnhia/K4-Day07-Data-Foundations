# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Xây dựng knowledge base về chính sách công khai của Shopee Việt Nam liên quan đến trả hàng/hoàn tiền, thanh toán, đăng bán sản phẩm, hàng cấm/hạn chế và vận chuyển; đánh giá ảnh hưởng của chunking và metadata đến retrieval.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách trả hàng và hoàn tiền | https://help.shopee.vn/portal/4/article/77251 | 2026-08-03 / not-stated | 1.113 | `both`, `returns-policy`, `vi` |
| 2 | Điều kiện và lý do trả hàng hoàn tiền | https://help.shopee.vn/portal/4/article/188931 | 2026-08-03 / not-stated | 894 | `buyer`, `return-conditions`, `vi` |
| 3 | Quy trình gửi yêu cầu trả hàng hoàn tiền | https://help.shopee.vn/portal/4/article/190242 | 2026-08-03 / not-stated | 856 | `buyer`, `return-process`, `vi` |
| 4 | Các phương thức thanh toán | https://help.shopee.vn/portal/article/1014?locale=vi_VN | 2026-08-03 / not-stated | 486 | `buyer`, `payment-methods`, `vi` |
| 5 | Điều kiện thanh toán COD | https://help.shopee.vn/portal/article/1013?locale=vi_VN | 2026-08-03 / not-stated | 496 | `buyer`, `payment-cod`, `vi` |
| 6 | Quy định đăng bán sản phẩm | https://help.shopee.vn/portal/4/article/77246 | 2026-08-03 / 2024-08-14 | 1.164 | `seller`, `seller-listing`, `vi` |
| 7 | Chính sách cấm và hạn chế sản phẩm | https://help.shopee.vn/portal/4/article/77247 | 2026-08-03 / not-stated | 1.035 | `seller`, `prohibited-products`, `vi` |
| 8 | Chính sách vận chuyển | https://help.shopee.vn/portal/4/article/77250 | 2026-08-03 / not-stated | 1.305 | `both`, `shipping-policy`, `vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu chỉ chứa 8 nguồn chính sách công khai của Shopee, không có dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata; danh mục nguồn một-một nằm tại `data/shopee_ecommerce/sources.csv`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `shopee-return-conditions` | Định danh duy nhất; truy vết chunk và xóa theo tài liệu. |
| `customer_role` | enum | `buyer`, `seller`, `both` | Lọc chính sách đúng đối tượng; bắt buộc cho K4. |
| `category` | string | `return-process`, `shipping-policy` | Phân vùng chủ đề, giảm nhiễu giữa các chính sách. |
| `source_url` | URL | `https://help.shopee.vn/...` | Kiểm chứng trực tiếp thông tin nguồn. |
| `retrieved_at` / `document_version` | date/string | `2026-08-03` / `2024-08-14` | Theo dõi độ mới và phiên bản của chính sách. |
| `language` | string | `vi` | Xác định ngôn ngữ của corpus/embedding. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Những lý do nào khiến Người mua có thể yêu cầu Trả hàng/Hoàn tiền? | Chưa nhận/thiếu hàng; sai hàng; bể vỡ, rò rỉ, bao bì hư; hàng lỗi, khác mô tả, đã qua sử dụng, giả hoặc nhái. | `shopee-return-conditions` — “Các lý do có thể được chấp nhận”. |
| 2 | Người mua cần chuẩn bị và gửi bằng chứng trả hàng/hoàn tiền như thế nào? | Chuẩn bị video mở kiện, ảnh sản phẩm/tem nhãn/kiện hàng; video liên tục, không cắt ghép, rõ mã vận đơn. Trong đơn hàng chọn Trả hàng/Hoàn tiền, chọn lý do, điền mô tả và tải ảnh/video để gửi. | `shopee-return-request-process` — “Bằng chứng nên chuẩn bị”, “Các bước gửi yêu cầu”. |
| 3 | Khi nào Người mua không thể chọn COD và cần làm gì? | COD chỉ áp dụng khi khu vực và sản phẩm/đơn hàng đủ điều kiện; nếu không đáp ứng điều kiện COD, Người mua phải chọn phương thức thanh toán khác. | `shopee-cod-eligibility` — “Thanh toán khi nhận hàng (COD)”. |
| 4 | Người bán phải mô tả sản phẩm như thế nào khi đăng bán? **Filter:** `customer_role=seller`. | Mô tả phải đầy đủ, chi tiết, trung thực, rõ ràng; nêu đặc điểm/công dụng/cách dùng/lưu ý, tình trạng hàng cũ, nguồn gốc, xuất xứ, thuộc tính và bảo hành theo yêu cầu; không đưa thông tin liên hệ để quảng cáo/dẫn sang web khác. | `shopee-seller-listing-policy` — “Thông tin đăng bán”. |
| 5 | Vi phạm chính sách hàng cấm/hạn chế có thể bị xử lý ra sao? **Filter:** `customer_role=seller`. | Shopee có thể xóa sản phẩm, giới hạn, đình chỉ hoặc xóa tài khoản, cấn trừ số dư/phong tỏa quyền rút tiền và áp dụng biện pháp khác theo chính sách hoặc pháp luật. | `shopee-prohibited-products-policy` — “Hậu quả vi phạm”. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
