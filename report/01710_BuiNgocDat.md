# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Bùi Ngọc Đạt
**Nhóm:** A6-1
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có hướng gần nhau, cho thấy hai đoạn văn có ngữ nghĩa hoặc ngữ cảnh tương tự. Giá trị càng gần 1 thì mức độ tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Khách hàng có thể đổi sản phẩm trong vòng 7 ngày.
- Câu B: Người mua được phép hoàn trả hàng trong 7 ngày kể từ khi nhận.
- Tại sao tương đồng: Cả hai cùng đề cập đến chính sách đổi/trả hàng và thời hạn 7 ngày.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Khách hàng có thể đổi sản phẩm trong vòng 7 ngày.
- Câu B: Nhiệt độ hôm nay ở Hà Nội là 35 độ C.
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau: chính sách mua sắm và thời tiết.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity đo hướng của các vector nên tập trung vào mức độ gần nhau về ngữ nghĩa. Độ dài văn bản hoặc độ lớn vector có thể khác nhau, vì vậy khoảng cách Euclid dễ bị ảnh hưởng hơn và thường kém phù hợp cho việc so sánh text embeddings.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)`
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi `overlap=100`, số chunk là `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`; tức tăng từ 23 lên 25 chunks. Overlap lớn hơn giữ thêm ngữ cảnh ở ranh giới hai chunk, hạn chế việc một ý hoặc câu bị cắt rời, nhưng làm tăng số embedding cần lưu trữ và chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách văn bản tại khoảng trắng đứng sau các dấu kết câu `.`, `!` và `?`, nhờ đó giữ lại dấu câu trong từng sentence. Sau khi loại bỏ khoảng trắng thừa và các phần tử rỗng, các câu được nhóm lại theo `max_sentences_per_chunk`. Với văn bản rỗng hoặc chỉ gồm khoảng trắng, hàm trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt các separator theo độ ưu tiên: đoạn văn (`\n\n`), dòng (`\n`), câu (`. `), từ (dấu cách), rồi cuối cùng mới cắt theo ký tự. Nếu một đoạn còn dài hơn `chunk_size`, `_split` gọi đệ quy với separator tiếp theo; trường hợp cơ sở là đoạn đã đủ ngắn hoặc đã không còn separator. Các đoạn nhỏ liền kề được ghép lại khi tổng độ dài vẫn nằm trong giới hạn để tránh tạo quá nhiều chunk ngắn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Khi thêm tài liệu, tôi tạo embedding cho `content` rồi lưu `id`, nội dung, metadata và vector embedding vào record; ưu tiên ChromaDB khi có sẵn, nếu không thì dùng danh sách trong bộ nhớ. Khi tìm kiếm, truy vấn cũng được embedding, sau đó tính dot product với từng vector đã lưu và sắp xếp kết quả theo điểm giảm dần. Với embedding đã chuẩn hoá, dot product tương ứng với cosine similarity.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc theo metadata trước khi tính điểm để chỉ xếp hạng các chunk thuộc đúng phạm vi, ví dụ đúng phòng ban hoặc ngôn ngữ. Tôi thêm `doc_id` vào metadata của mỗi chunk để liên kết chúng với tài liệu gốc. `delete_document` tìm và xoá toàn bộ record có `metadata['doc_id']` trùng với mã tài liệu được yêu cầu.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` truy xuất các chunk có điểm cao nhất bằng `store.search(question, top_k)`, đánh số chúng và ghép thành phần `Context`. Prompt gồm chỉ dẫn chỉ dùng thông tin trong context, ngữ cảnh đã truy xuất, câu hỏi và vị trí `Answer`. Prompt này được truyền vào `llm_fn` để sinh câu trả lời có căn cứ từ tài liệu.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
python -m pytest tests/ -v
platform win32 -- Python 3.12.8, pytest-9.1.1
collected 42 items

======================== 42 passed, 1 warning in 0.18s ========================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
