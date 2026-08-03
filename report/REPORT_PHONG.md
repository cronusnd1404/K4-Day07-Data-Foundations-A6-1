# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đào Việt Phong  
**Nhóm:** A6-1
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, tức là hai văn bản mang ý nghĩa hoặc nội dung giống nhau hơn so với các cặp khác.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi thích ăn phở vào buổi sáng."
- Câu B: "Buổi sáng tôi thường ăn phở."
- Tại sao tương đồng: cả hai câu đều mô tả cùng một hành động ăn phở vào buổi sáng, nên nội dung và ngữ nghĩa rất giống nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi thích ăn phở vào buổi sáng."
- Câu B: "Máy tính được sử dụng để xử lý dữ liệu." 
- Tại sao khác: nội dung của hai câu hoàn toàn khác nhau, một câu nói về ăn uống và một câu nói về công nghệ.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity đo góc giữa hai vector và do đó bỏ qua độ dài vector, nên phù hợp với text embeddings vì nó tập trung vào hướng ngữ nghĩa thay vì kích thước tuyệt đối của embedding.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Với `chunk_size=500` và `overlap=50`, mỗi bước dịch là `500 - 50 = 450` ký tự. Do đó số chunk là `ceil(10000 / 450) = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Nếu overlap tăng lên 100, bước dịch còn `500 - 100 = 400`, nên số chunk tăng lên khoảng `ceil(10000 / 400) = 25`. Overlap lớn hơn giúp giữ lại nhiều ngữ cảnh giữa các chunk liên tiếp, điều này thường cải thiện khả năng truy xuất và trả lời vì phần thông tin quan trọng không bị cắt rời.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex để tách câu theo các dấu chấm, chấm than, chấm hỏi kèm theo khoảng trắng, đồng thời cũng xử lý trường hợp `'.\n'`. Sau khi tách câu, tôi gom mỗi nhóm không quá `max_sentences_per_chunk` câu, và loại bỏ khoảng trắng thừa để tránh chunk rỗng hoặc có dấu cách đầu/cuối.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán dùng một danh sách separator theo thứ tự ưu tiên, ví dụ `['\n\n', '\n', '. ', ' ', '']`. Với mỗi mức separator, nếu đoạn văn dài hơn `chunk_size` thì chia nhỏ theo separator đó và đệ quy vào từng phần con. Base case xảy ra khi đoạn ngắn hơn `chunk_size` hoặc không còn separator, khi đó trả về đoạn hiện tại làm một chunk.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi lưu mỗi document dưới dạng record gồm `id`, `content`, `metadata`, và `embedding` được tính bằng hàm nhúng. Khi tìm kiếm, tôi tạo embedding của truy vấn rồi tính độ tương tự cosine hoặc dot product giữa truy vấn và từng embedding đã lưu, sau đó sắp xếp và trả về top-k kết quả có score cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi áp dụng metadata filter trước khi tính similarity để chỉ tìm trong các record phù hợp. Với `delete_document`, tôi loại bỏ mọi record liên quan đến `doc_id` đã cho và trả về `True` nếu có bản ghi bị xóa, hoặc `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tôi lấy top-k chunk liên quan từ store, xây dựng prompt bằng cách ghép các chunk này vào phần context, rồi đặt câu hỏi cuối prompt. Sau đó gọi `llm_fn(prompt)` để tạo câu trả lời dựa trên ngữ cảnh đã được inject, và trả kết quả trả về cho người dùng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** 11 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Embeddings thường biểu diễn ý nghĩa dựa trên hướng của vector, vì vậy một số cặp câu có mặt chữ khác nhưng vẫn có ngữ nghĩa tương tự có thể nhận được score cao. Điều bất ngờ thường là khi hai câu có từ khác nhau nhưng cùng ý nghĩa vẫn được đánh giá gần nhau, cho thấy embeddings bắt được ngữ nghĩa chung thay vì chỉ so sánh từng từ.

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
> Một điều học được là cách chọn bộ câu hỏi đánh giá và cách xếp hạng chunk rất quan trọng để hệ retrieval hoạt động hiệu quả. Một số nhóm khác tập trung vào việc giữ ngữ cảnh chunk tốt hơn và tạo prompt rõ ràng cho agent.

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
