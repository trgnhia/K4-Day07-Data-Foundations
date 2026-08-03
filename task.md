# Phân công công việc nhóm — Lab 7

## Mục tiêu chung

Hoàn thành đánh giá retrieval trên corpus chung `data/shopee_ecommerce/` gồm 8 chính sách công khai của Shopee Việt Nam. Cả nhóm dùng cùng 5 benchmark query/gold answer trong `report/REPORT_NHOM.md`, nhưng **mỗi người tự làm và chạy code trong thư mục cá nhân; không chia sẻ code Task 1–3**.

## Quy ước chung

- Corpus chuẩn: `data/shopee_ecommerce/`; không dùng `data/k4_ecommerce/` để benchmark hoặc demo.
- Mỗi người dùng `EMBEDDING_PROVIDER=local` khi đánh giá chất lượng retrieval; mock embedding chỉ dùng cho unit test.
- Mỗi người nộp kết quả cho **cả 5 query**: top-3 chunks, score, đánh giá relevance và tóm tắt câu trả lời agent.
- Câu 4 và 5 bắt buộc chạy `search_with_filter(..., metadata_filter={"customer_role": "seller"})`.
- Mọi người cập nhật phần kết quả/nhận xét của mình đúng hạn; nhóm trưởng tích hợp, không nhận code từ thành viên khác.

---

## Thành viên 1 — Trần Đại Nghĩa (Nhóm trưởng)

### Trách nhiệm chính

1. Quản lý corpus, kiểm tra `sources.csv`, metadata, nguồn công khai và tính truy vết của 8 tài liệu.
2. Chốt 5 benchmark query/gold answer trong `REPORT_NHOM.md`; không thay đổi query sau khi nhóm bắt đầu đo trừ khi cả nhóm thống nhất.
3. Tự triển khai/chạy chiến lược **custom chunk theo heading/section** hoặc `RecursiveChunker` được tinh chỉnh trong folder cá nhân.
4. Chạy đủ 5 benchmark bằng local embedder; thực hiện demo search buyer, search seller có metadata filter và `KnowledgeBaseAgent.answer()`.
5. Tổng hợp kết quả của 5 người, phân tích chiến lược tốt nhất, failure case và hoàn thiện `REPORT_NHOM.md`.
6. Chuẩn bị, điều phối và trình bày demo.

### Đầu ra phải bàn giao

- Bảng kết quả 5 query của chiến lược cá nhân.
- `REPORT_NHOM.md` hoàn chỉnh: corpus, baseline, 5 chiến lược, benchmark, bảng tổng hợp, failure analysis và demo script.
- Kịch bản demo 5–7 phút.

---

## Thành viên 2 — Chiến lược SentenceChunker

### Việc cần làm

1. Tự làm Task 1–3 trong folder cá nhân, không nhận/chia code.
2. Dùng `SentenceChunker(max_sentences_per_chunk=2)` trên corpus chung.
3. Nạp corpus, chạy 5 benchmark query với local embedder; câu 4 và 5 dùng seller filter.
4. Ghi nhận số chunk, độ dài trung bình, top-3, score và ưu/nhược điểm của chunk theo câu.

### Đầu ra phải bàn giao

- Bảng kết quả 5 query.
- Một nhận xét: chunk theo câu bảo toàn ý như thế nào và ở query nào bị thiếu ngữ cảnh.

---

## Thành viên 3 — Chiến lược RecursiveChunker

### Việc cần làm

1. Tự làm Task 1–3 trong folder cá nhân, không nhận/chia code.
2. Dùng `RecursiveChunker(chunk_size=400)` trên corpus chung.
3. Chạy 5 benchmark query bằng local embedder, bao gồm seller filter cho câu 4 và 5.
4. So sánh độ mạch lạc của chunk giữa heading, đoạn văn và câu; xác định ít nhất một kết quả không tốt.

### Đầu ra phải bàn giao

- Bảng kết quả 5 query.
- Một failure case: query, top-3 nhận được, nguyên nhân và đề xuất cải thiện.

---

## Thành viên 4 — Chiến lược FixedSize (baseline)

### Việc cần làm

1. Tự làm Task 1–3 trong folder cá nhân, không nhận/chia code.
2. Dùng `FixedSizeChunker(chunk_size=400, overlap=50)` làm baseline.
3. Chạy 5 benchmark query bằng local embedder; câu 4 và 5 dùng seller filter.
4. Ghi số chunk, độ dài trung bình và kiểm tra overlap có giữ được ngữ cảnh ở ranh giới không.

### Đầu ra phải bàn giao

- Bảng kết quả 5 query.
- Nhận xét so sánh baseline fixed-size với chiến lược có ranh giới ngữ nghĩa.

---

## Thành viên 5 — FixedSize tinh chỉnh + kiểm tra đánh giá

### Việc cần làm

1. Tự làm Task 1–3 trong folder cá nhân, không nhận/chia code.
2. Dùng `FixedSizeChunker(chunk_size=700, overlap=100)` để so sánh với baseline của thành viên 4.
3. Chạy 5 benchmark query bằng local embedder; câu 4 và 5 dùng seller filter.
4. Đối chiếu top-3 với gold answer, đánh dấu `relevant`/`not relevant` và kiểm tra score có phân biệt được kết quả đúng với nhiễu không.
5. Hỗ trợ nhóm trưởng rà bảng tổng hợp, đặc biệt phần metadata filter và failure case.

### Đầu ra phải bàn giao

- Bảng kết quả 5 query.
- Bảng đối chiếu filtered và unfiltered cho ít nhất một câu seller.
- Nhận xét về đánh đổi giữa chunk lớn hơn và overlap lớn hơn.

---

## Mốc thực hiện

1. **Checkpoint cá nhân:** mỗi thành viên hoàn thành Task 1–3, tự chạy test trong folder cá nhân.
2. **Chạy benchmark:** mọi người dùng cùng corpus và 5 query, nhưng chạy độc lập bằng code/strategy cá nhân.
3. **Bàn giao kết quả:** gửi bảng 5 query + nhận xét cho nhóm trưởng.
4. **Tổng hợp:** nhóm trưởng điền các bảng còn lại của `REPORT_NHOM.md`.
5. **Demo:** chạy lại strategy của nhóm trưởng, một truy vấn buyer, một truy vấn seller có filter, câu trả lời agent và bảng so sánh 5 strategy.
