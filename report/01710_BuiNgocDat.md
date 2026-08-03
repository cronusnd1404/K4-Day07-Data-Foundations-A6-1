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
| 1 | Người mua được trả hàng khi nhận sai màu sản phẩm. | Khách hàng có thể yêu cầu hoàn tiền nếu hàng giao sai màu. | cao | 0.0567 | Không |
| 2 | Apple Pay có giới hạn thanh toán cho mỗi đơn hàng. | Apple Pay hỗ trợ giá trị đơn hàng tối đa 25.000.000 VNĐ. | cao nhất | 0.1115 | Có |
| 3 | Nhà bán không được đăng hàng đã qua sử dụng. | Tiki không hỗ trợ hàng cũ hoặc second hand. | cao | -0.1179 | Không |
| 4 | Giao hàng hỏa tốc áp dụng tại nội thành Hà Nội. | Chính sách bảo mật cho phép chia sẻ dữ liệu theo yêu cầu pháp luật. | thấp | -0.1238 | Có |
| 5 | Khách hàng nhận hàng rồi thanh toán COD. | Thời tiết Hà Nội hôm nay nắng nóng. | thấp nhất | -0.0265 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 3 có nghĩa rất gần nhau nhưng lại nhận điểm âm, trong khi cặp 2 là cặp cao nhất. Các điểm trên được tạo bởi `MockEmbedder` xác định (hash-based) để kiểm thử hàm `compute_similarity`, nên không phản ánh ngữ nghĩa tiếng Việt và không được dùng để chọn chiến lược retrieval. Kết luận retrieval của nhóm bên dưới dựa trên lần chạy với `text-embedding-3-small` trong `REPORT_NHOM.md`.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Nếu người bán giao sai kích cỡ hoặc màu sản phẩm thì tôi có được yêu cầu trả hàng không? | Mục điều kiện trả hàng/hoàn tiền của Shopee nêu trường hợp giao sai kích cỡ, màu sắc. | 0.3565 | Có | Có thể yêu cầu trả hàng/hoàn tiền khi người bán giao sai kích cỡ hoặc màu. |
| 2 | Dịch vụ giao hàng hỏa tốc 4 giờ của Lazada áp dụng cho khu vực nào và giới hạn khối lượng sản phẩm là bao nhiêu? | Mục giao hàng hỏa tốc Lazada nêu khu vực, khối lượng và kích thước áp dụng. | 0.5515 | Có | Áp dụng nội thành Hà Nội và TP.HCM; hàng dưới 15 kg, dưới 70 cm, trừ bỉm/tã. |
| 3 | Nhà bán có được đăng bán hàng cũ, đã qua sử dụng trên sàn không? | Mục hàng hóa cấm/hạn chế của Tiki, truy xuất với `customer_role=seller`. | 0.3156 | Có | Không; Tiki không hỗ trợ hàng cũ, đã qua sử dụng, like new hoặc second hand. |
| 4 | Nếu dùng Apple Pay để thanh toán thì giá trị đơn hàng tối đa được hỗ trợ là bao nhiêu? | Mục Apple Pay trong chính sách phương thức thanh toán Shopee. | 0.6565 | Có | Giá trị tối đa là 25.000.000 VNĐ (mức hỗ trợ từ 10.000đ). |
| 5 | Sàn có chia sẻ dữ liệu cá nhân của tôi với cơ quan chính phủ không? | Mục chia sẻ dữ liệu với bên thứ ba trong chính sách bảo mật Shopee. | 0.3480 | Có | Có, trong trường hợp có yêu cầu theo pháp luật. |

> Kết quả trên dùng `HeadingSectionChunker` và embedder OpenAI `text-embedding-3-small`, cùng corpus/benchmark của nhóm. Điểm số và khả năng chứa chunk liên quan trong top-3 được đối chiếu với bảng tổng hợp tại `REPORT_NHOM.md`.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Với tài liệu chính sách có heading rõ ràng, chia theo heading giữ được trọn một điều khoản và thường tốt hơn cắt theo số ký tự cố định. Tôi cũng học được rằng metadata filter nên được áp dụng trước retrieval: ở câu hỏi dành cho người bán, lọc `customer_role=seller` loại bỏ các chunk dành cho người mua và giảm nhiễu đáng kể.

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
