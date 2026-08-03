# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Shopee Policy Retrieval — K4
**Thành viên:** 
 Trần Đại Nghĩa (2A202601328)
 Vũ Quang Huy (2A202601412)
 Nguyễn Hoàng Sơn (2A202601939)
 Nguyễn Đức Mạnh (2A202601176)
 Thiều Thị Ngọc Anh (2A202601864)
**Ngày:** 03/08/2026

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
| `return-request-process` | FixedSize (`chunk_size=400`) | 3 | 285.3 | Có, nhưng có thể cắt giữa section. |
| `return-request-process` | Sentence (`3 câu/chunk`) | 4 | 211.8 | Có; phù hợp quy trình ngắn. |
| `return-request-process` | Recursive (`chunk_size=400`) | 7 | 120.6 | Có ranh giới tự nhiên, nhưng tạo nhiều chunk nhỏ. |
| `seller-listing-policy` | FixedSize (`chunk_size=400`) | 3 | 388.0 | Một số section có thể bị cắt. |
| `seller-listing-policy` | Sentence (`3 câu/chunk`) | 4 | 288.0 | Giữ câu nhưng chưa giữ được heading. |
| `seller-listing-policy` | Recursive (`chunk_size=400`) | 10 | 114.6 | Giữ đoạn/câu, nhưng phân mảnh mạnh. |
| `shipping-policy` | FixedSize (`chunk_size=400`) | 4 | 326.2 | Có thể cắt điều kiện đóng gói. |
| `shipping-policy` | Sentence (`3 câu/chunk`) | 3 | 432.3 | Mạch lạc nhưng chunk dài hơn. |
| `shipping-policy` | Recursive (`chunk_size=400`) | 7 | 184.7 | Cân bằng giữa ranh giới đoạn và độ dài. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Trần Đại Nghĩa**
- **Loại chiến lược:** custom `HeadingSectionChunker(chunk_size=650)`.
- **Mô tả & lý do chọn:** Corpus đã được chuẩn hóa Markdown theo tiêu đề/section. Chunker giữ tiêu đề chính sách cùng điều khoản phía dưới, loại bỏ chunk chỉ có heading; vì vậy câu hỏi về điều kiện, quy trình và hậu quả vẫn giữ được ngữ cảnh. Corpus 8 tài liệu tạo 23 chunks.

**Thành viên 2 — Vũ Quang Huy**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=400)`.
- **Mô tả & lý do chọn:** Tách ưu tiên theo đoạn, xuống dòng, câu và từ để hạn chế cắt ngang câu. Corpus tạo 28 chunks; phương án này đặc biệt phù hợp khi chính sách có các đoạn/liệt kê dài.
- **Lưu ý đo lường:** Kết quả hiện dùng `MockEmbedder` do lỗi môi trường AppLocker, nên chỉ dùng để phân tích cấu trúc chunk/filter, không so sánh trực tiếp score với local embedder.

**Thành viên 3 — Nguyễn Hoàng Sơn**
- **Loại chiến lược:** Chưa ghi cấu hình chunker trong file kết quả đã merge.
- **Mô tả & lý do chọn:** Có kết quả chạy `LocalEmbedder`, 5 query chuẩn, A/B metadata filter và phân tích failure case. Thành viên cần bổ sung chính xác loại chunker, tham số và số chunks trước khi chốt bảng so sánh.

**Thành viên 4 — Nguyễn Đức Mạnh**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=400, overlap=50)`.
- **Mô tả & lý do chọn:** Là baseline cố định có overlap để kiểm tra đánh đổi giữa số chunks và việc bảo toàn ngữ cảnh ở ranh giới.
- **Trạng thái:** Đã merge script benchmark dùng đúng 5 query chuẩn, nhưng chưa có output/top-3/score để tổng hợp.

**Thành viên 5 — Thiều Thị Ngọc Anh**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=700, overlap=100)`.
- **Mô tả & lý do chọn:** Chunk lớn hơn và overlap lớn hơn để so sánh với baseline 400/50; lần chạy ghi nhận 15 chunks, độ dài trung bình 536.6 ký tự.
- **Trạng thái:** Output hiện dùng MockEmbedder và bộ 5 query khác benchmark nhóm; cần chạy lại đúng 5 query đã chốt bằng local embedder để dùng trong tổng hợp.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trần Đại Nghĩa | Heading/section custom, 650; local | 10 (5/5 top-3) | Heading đi cùng nội dung, 23 chunks, cả 5 query có chunk liên quan. | Query bằng chứng có chunk đúng ở hạng 3. |
| Vũ Quang Huy | Recursive, 400; mock | Chưa chấm bằng local (5/5 top-3 theo mock) | Bảo toàn ranh giới đoạn/câu; filter giảm ứng viên từ 28 xuống 8. | Mock không phản ánh ngữ nghĩa; query 1 có top-1 nhiễu. |
| Nguyễn Hoàng Sơn | Cấu hình chunker chờ bổ sung; local | 6 (tự chấm theo rubric) | Có A/B filter và đánh giá ở cấp chunk. | Query bằng chứng không có chunk video ở top-3; thiếu thông tin cấu hình. |
| Nguyễn Đức Mạnh | Fixed size, 400/50 | Chờ output | Baseline có overlap, dùng đúng query chuẩn trong script. | Chưa có bảng top-3/score/relevance. |
| Thiều Thị Ngọc Anh | Fixed size, 700/100; mock | Chờ chạy lại | Có thống kê 15 chunks và so sánh với baseline. | Sai bộ query chuẩn, fallback mock; chưa có agent answer/relevance cho 5 query nhóm. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **Kết luận tạm thời:** Heading/section custom của Trần Đại Nghĩa là chiến lược tốt nhất trong các kết quả local đã có cấu hình đầy đủ: 5/5 query có chunk liên quan trong top-3 và filter seller trả đúng tập chính sách. Tuy nhiên, chưa thể chốt so sánh cuối cùng khi Mạnh và Anh chưa chạy lại benchmark chuẩn, còn Huy dùng mock; nhóm sẽ cập nhật kết luận sau khi đủ năm output local.

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
| 1 | Lý do Trả hàng/Hoàn tiền | Tạm: Heading/section custom (local) | Có | Chunk `return-conditions` ở top-3; cần xem thêm FixedSize 400/50 và 700/100. |
| 2 | Bằng chứng và quy trình gửi yêu cầu | Tạm: Heading/section custom (local) | Có | Chunk quy trình ở hạng 3; đây là failure case nhẹ. |
| 3 | Điều kiện COD | Tạm: Heading/section custom (local) | Có | `cod-eligibility` ở top-1. |
| 4 | Mô tả sản phẩm seller | Tạm: Heading/section custom (local) | Có | Filter seller trả listing policy ở top-1. |
| 5 | Xử lý vi phạm hàng cấm | Tạm: Heading/section custom (local) | Có | Filter seller trả prohibited-products policy ở top-1. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có. Với query 4 và 5, filter `customer_role=seller` loại toàn bộ tài liệu buyer-only (đổi trả/thanh toán) trước khi xếp hạng. Kết quả local của Nghĩa và Sơn đều cho top-1 thuộc `seller-listing-policy` hoặc `prohibited-products-policy`; kết quả Recursive của Huy cũng cho thấy không gian ứng viên giảm từ 28 xuống 8 chunks.

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
