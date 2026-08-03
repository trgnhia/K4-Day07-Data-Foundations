# Bao Cao Ca Nhan - Lab 7: Embedding & Vector Store

**Ho ten:** Vu Quang Huy  
**Ma sinh vien:** K4-2A202601412  
**Ngay:** 2026-08-03

---

## 1. Khoi Dong - Ca Nhan

### Bai tap 1.1 - Cosine Similarity

**Cosine similarity cao nghia la gi?**  
Khi hai doan van ban co cosine similarity cao, vector embedding cua chung tro cung mot huong. Dieu nay thuong co nghia la hai van ban gan nhau ve chu de, y dinh hoac ngu nghia, ngay ca khi khong dung y het cac tu giong nhau.

**Vi du do tuong tu cao:**
- Cau A: Khach hang co the doi tra san pham trong 7 ngay neu hang bi loi.
- Cau B: Neu san pham loi, nguoi mua duoc yeu cau hoan tra trong vong mot tuan.
- Giai thich: Hai cau cung noi ve dieu kien doi tra san pham loi va moc thoi gian 7 ngay.

**Vi du do tuong tu thap:**
- Cau A: He thong ho tro thanh toan bang the ngan hang.
- Cau B: Cong thuc nau pho bo can nuoc dung trong va thom.
- Giai thich: Hai cau thuoc hai mien noi dung khac nhau, mot cau ve thanh toan TMĐT va mot cau ve nau an.

**Tai sao dung cosine similarity thay vi Euclidean distance cho text embeddings?**  
Cosine similarity tap trung vao huong cua vector, nen phu hop de so sanh y nghia cua van ban. Euclidean distance bi anh huong nhieu boi do lon vector, trong khi voi text embeddings ta thuong quan tam hai van ban co gan nhau ve ngu nghia hay khong.

### Bai tap 1.2 - Chunking math

Voi tai lieu 10,000 ky tu, `chunk_size=500`, `overlap=50`:

```text
so chunk = ceil((10000 - 50) / (500 - 50))
         = ceil(9950 / 450)
         = ceil(22.11)
         = 23 chunks
```

Neu tang `overlap=100`:

```text
so chunk = ceil((10000 - 100) / (500 - 100))
         = ceil(9900 / 400)
         = ceil(24.75)
         = 25 chunks
```

So chunk tang tu 23 len 25 vi buoc truot moi lan nho hon. Tang overlap giup giu lai ngu canh o bien giua hai chunk, huu ich khi mot y quan trong bi cat ngang tai ranh gioi chunk.

---

## 2. Huong Tiep Can Cua Toi

### `SentenceChunker.chunk`

Toi dung regex `(?<=[.!?])\s+` de cat van ban tai khoang trang nam sau dau ket thuc cau. Sau khi tach, cac cau rong duoc loai bo, roi nhom toi da `max_sentences_per_chunk` cau vao moi chunk. Truong hop text rong tra ve danh sach rong.

### `RecursiveChunker.chunk` va `_split`

Toi trien khai chia de quy theo thu tu separator: doan van, dong, cau, tu, roi fallback cat co dinh neu khong con separator phu hop. Base case la text rong hoac text da ngan hon `chunk_size`. Khi mot phan van ban van qua dai, ham tiep tuc thu separator tiep theo.

### `compute_similarity`

Ham tinh cosine similarity bang cong thuc `dot(a, b) / (||a|| * ||b||)`. Neu mot trong hai vector co norm bang 0, ham tra ve `0.0` de tranh loi chia cho 0.

### `ChunkingStrategyComparator`

Comparator chay ca ba chien luoc `FixedSizeChunker`, `SentenceChunker`, `RecursiveChunker`. Voi moi chien luoc, toi tra ve so chunk, do dai trung binh, do dai nho nhat/lon nhat va danh sach chunk de co the so sanh truc tiep.

### `EmbeddingStore`

Toi dung in-memory store de dam bao test chay on dinh va khong phu thuoc ChromaDB. Moi document duoc luu voi `id`, `content`, `metadata`, `embedding`; metadata tu dong co `doc_id` neu chua co. Search embed query, tinh dot product voi tung embedding, sap xep score giam dan va cat theo `top_k`.

### `search_with_filter` va `delete_document`

`search_with_filter` loc metadata truoc, sau do moi search tren tap ung vien da loc. `delete_document` xoa tat ca record co `id` trung voi `doc_id` hoac metadata `doc_id` trung voi gia tri can xoa.

### `KnowledgeBaseAgent.answer`

Agent truy xuat top-k chunk lien quan, ghep chunk vao prompt theo dang context co score, sau do goi `llm_fn(prompt)`. Prompt yeu cau chi tra loi dua tren context va noi ro neu context khong du thong tin.

---

## 3. Hoan Thien Code - Ket Qua Kiem Thu

Lenh da chay:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ -v
```

Ket qua tom tat:

```text
collected 42 items
42 passed in 0.19s
```

**So luong bai test vuot qua:** 42 / 42

---

## 4. Du Doan Do Tuong Tu

Embedding dung cho bang nay la `_mock_embed`, vi vay diem so co tinh xac dinh nhung khong phan anh chat luong ngu nghia tieng Viet nhu embedder that.

| Cap | Cau A | Cau B | Du doan | Diem thuc te | Dung? |
|---|---|---|---|---:|---|
| 1 | Doi tra hang trong 7 ngay | Khach co the hoan hang trong vong 7 ngay | Cao | 0.2226 | Dung |
| 2 | Phi van chuyen duoc tinh theo khu vuc | Cuoc giao hang phu thuoc vao dia chi nhan | Cao | 0.0274 | Gan dung |
| 3 | Nguoi ban phai cung cap thong tin san pham chinh xac | Mo ta san pham can dung su that | Cao | -0.0647 | Sai |
| 4 | Chinh sach bao mat du lieu ca nhan | Cong thuc nau pho bo truyen thong | Thap | -0.1008 | Dung |
| 5 | Thanh toan bang the ngan hang | Thoi tiet hom nay co mua khong | Thap | -0.2119 | Dung |

Ket qua bat ngo nhat la cap 3 co y nghia rat gan nhau nhung diem lai am. Nguyen nhan la mock embedding sinh vector xac dinh theo chuoi, khong hieu ngu nghia that; vi vay no phu hop cho unit test hon la danh gia retrieval thuc te.

---

## 5. Ket Qua Truy Xuat Cua Toi

Toi chay 5 query demo tren bo tai lieu ngan ve chinh sach TMĐT. Do van dung `_mock_embed`, mot so ket qua top-1 khong phai ket qua ngu nghia tot nhat; phan nay chu yeu xac minh pipeline search, filter va agent da chay dung.

| # | Cau hoi | Top-1 chunk truy xuat duoc | Score | Lien quan? | Cau tra loi Agent |
|---|---|---|---:|---|---|
| 1 | Khi nao khach hang duoc doi tra san pham? | Khach hang co the yeu cau doi tra trong 7 ngay neu san pham loi, sai mo ta hoac giao nham. | 0.0617 | Co | Tra loi dua tren chunk truy xuat trong prompt. |
| 2 | Phi van chuyen phu thuoc vao yeu to nao? | He thong ho tro thanh toan bang the ngan hang, vi dien tu va thanh toan khi nhan hang neu kha dung. | 0.1765 | Khong | Tra loi dua tren chunk truy xuat trong prompt. |
| 3 | Co the thanh toan bang nhung phuong thuc nao? | He thong ho tro thanh toan bang the ngan hang, vi dien tu va thanh toan khi nhan hang neu kha dung. | 0.1845 | Co | Tra loi dua tren chunk truy xuat trong prompt. |
| 4 | Nguoi ban can lam gi khi dang san pham? | Khach hang co the yeu cau doi tra trong 7 ngay neu san pham loi, sai mo ta hoac giao nham. | 0.2512 | Khong | Tra loi dua tren chunk truy xuat trong prompt. |
| 5 | Du lieu ca nhan duoc su dung cho muc dich gi? | Du lieu ca nhan chi duoc dung de xu ly don hang, cham soc khach hang va tuan thu quy dinh bao mat. | 0.0849 | Co | Tra loi dua tren chunk truy xuat trong prompt. |

**So cau hoi tra ve chunk lien quan trong top-1:** 3 / 5  
**Ghi chu:** Khi chay giai doan so sanh that, nen dat `EMBEDDING_PROVIDER=local` de dung embedding da ngon ngu thay cho mock embedding.

Dieu toi hoc duoc la chat luong retrieval khong chi phu thuoc code search dung, ma phu thuoc rat lon vao embedding backend, cach chia chunk va metadata. Metadata filter huu ich khi cau hoi co pham vi ro, vi no giam nhieu ung vien nhieu truoc khi tinh score.

---

## Tu Danh Gia

| Tieu chi | Diem tu danh gia |
|---|---:|
| Khoi dong | 5 / 5 |
| Huong tiep can cua toi | 10 / 10 |
| Hoan thien code | 30 / 30 |
| Du doan do tuong tu | 5 / 5 |
| Ket qua truy xuat cua toi | 7 / 10 |
| **Tong phan ca nhan** | **57 / 60** |
