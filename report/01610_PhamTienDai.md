# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Tiến Đại
**Nhóm:** A6-1
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding gần như "cùng hướng" trong không gian nhiều chiều, tức hai đoạn văn bản mang ý nghĩa/ngữ cảnh gần giống nhau, bất kể độ dài câu chữ khác nhau đến đâu.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Người mua có thể đổi trả sản phẩm bị lỗi trong vòng 7 ngày."
- Câu B: "Khách hàng được hoàn tiền nếu sản phẩm giao không đúng mô tả."
- Tại sao tương đồng: cả hai đều nói về cùng chủ đề "chính sách đổi trả/hoàn tiền do lỗi từ người bán", chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sản phẩm bị cấm không được phép đăng bán trên sàn."
- Câu B: "Mèo là loài động vật được nhiều người nuôi làm thú cưng."
- Tại sao khác: hai câu không liên quan chủ đề, không chia sẻ ngữ cảnh hay từ khóa ngữ nghĩa nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ quan tâm đến *hướng* của vector (ý nghĩa) mà bỏ qua *độ lớn* (magnitude), vốn thường bị ảnh hưởng bởi độ dài văn bản hoặc cách chuẩn hóa embedding. Nhờ vậy, hai đoạn văn cùng ý nghĩa nhưng độ dài khác nhau (một câu ngắn, một đoạn dài) vẫn được nhận diện là gần nhau, trong khi Euclidean distance dễ bị lệch bởi norm của vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính:
> `số_chunk = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> Đáp án: **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks` — tăng từ 23 lên 25 chunks (bước trượt `step = chunk_size - overlap` nhỏ lại nên cần nhiều chunk hơn để phủ hết văn bản). Overlap lớn hơn giúp giảm rủi ro cắt đứt một câu/ý quan trọng ngay tại ranh giới hai chunk, nhờ đó ngữ cảnh liền mạch hơn khi truy xuất, đổi lại tốn thêm bộ nhớ/embedding calls.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Cách tiếp cận khi lập trình các phần chính trong gói `src_Dai`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split` với lookbehind `(?<=[.!?])` theo sau khoảng trắng (và một biến thể xử lý dấu chấm trước xuống dòng) để tách câu mà vẫn giữ dấu câu ở cuối mỗi câu. Sau khi tách, loại bỏ chuỗi rỗng/khoảng trắng thừa bằng `strip()`, rồi gom nhóm `max_sentences_per_chunk` câu liên tiếp thành một chunk bằng cách duyệt danh sách theo bước nhảy (`step`). Edge case xử lý: văn bản rỗng trả về `[]` ngay từ đầu; `max_sentences_per_chunk` luôn được ép về tối thiểu 1 trong `__init__` để tránh vòng lặp vô hạn/chia cho 0.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử tách văn bản theo separator ưu tiên cao nhất trong danh sách (`\n\n`, `\n`, `. `, `" "`, `""`); với mỗi piece thu được, gộp dần vào `buffer` miễn còn nằm trong `chunk_size`. Khi một piece khiến buffer vượt kích thước, buffer hiện tại được chốt thành 1 chunk; nếu bản thân piece đó *vẫn* lớn hơn `chunk_size`, hàm đệ quy gọi lại `_split` trên piece đó với danh sách separator còn lại (tách mịn hơn) thay vì bỏ sót phần văn bản. Base case: hết separator (`remaining_separators` rỗng) thì trả nguyên `current_text` làm 1 chunk duy nhất, chấp nhận vượt `chunk_size` còn hơn mất dữ liệu. Ở cuối vòng lặp, `buffer` còn dư luôn được append trước khi `return`, tránh lỗi rơi ra ngoài hàm mà không trả kết quả.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ in-memory bằng `list[dict]` (`self._store`), mỗi record gồm `id`, `content`, `embedding` (gọi `self._embedding_fn(content)` một lần khi add) và `metadata`. Khi `search`, embed câu truy vấn một lần, sau đó tính `compute_similarity` (cosine) giữa vector truy vấn và embedding của từng record đã lưu, sắp xếp giảm dần theo score và cắt lấy `top_k`, gắn thêm khóa `"score"` vào từng kết quả trả về.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc **trước**: `search_with_filter` duyệt `self._store`, chỉ giữ lại các record có toàn bộ cặp `key: value` trong `metadata_filter` khớp với `record["metadata"]`, rồi mới gọi lại hàm tìm kiếm nội bộ (`_search_records`) trên tập đã lọc — nhờ vậy độ phức tạp tính similarity giảm theo đúng tỉ lệ tài liệu được lọc. `delete_document` xóa bằng cách rebuild `self._store` qua list comprehension, giữ lại mọi record có `record["id"] != doc_id`, rồi so sánh độ dài trước/sau để trả về `True/False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `__init__` chỉ lưu tham chiếu tới `store` và `llm_fn`. `answer` gọi `store.search(question, top_k=top_k)` để lấy các chunk liên quan nhất, nối nội dung (`content`) của chúng bằng `"\n"` thành một khối `context`, rồi dựng prompt dạng `"Context:\n{context}\n\nQuestion: {question}\nAnswer:"` — cấu trúc đơn giản, tách rõ phần ngữ cảnh và câu hỏi để LLM dễ bám vào context khi trả lời (retrieval-augmented generation cơ bản).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts =============================
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker (7 tests) PASSED
tests/test_solution.py::TestSentenceChunker (4 tests) PASSED
tests/test_solution.py::TestRecursiveChunker (4 tests) PASSED
tests/test_solution.py::TestEmbeddingStore (8 tests) PASSED
tests/test_solution.py::TestKnowledgeBaseAgent (2 tests) PASSED
tests/test_solution.py::TestComputeSimilarity (4 tests) PASSED
tests/test_solution.py::TestCompareChunkingStrategies (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument (3 tests) PASSED

============================= 42 passed in 0.27s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Chạy `compute_similarity()` trên 5 cặp câu, embedding bằng `MockEmbedder` (hash-based, không mang ngữ nghĩa thật — dùng đúng mục đích cảnh báo trong đề bài).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Người mua có thể đổi trả sản phẩm bị lỗi trong vòng 7 ngày." | "Khách hàng được hoàn tiền nếu sản phẩm giao không đúng mô tả." | cao | 0.2402 | Không (dự đoán cao nhưng thực tế chỉ trung bình-thấp) |
| 2 | "Người bán phải cung cấp thông tin sản phẩm chính xác." | "Hôm nay trời nắng đẹp và tôi đi dạo công viên." | thấp | -0.0271 | Đúng (gần 0, không liên quan) |
| 3 | "Thanh toán khi nhận hàng (COD) là hình thức phổ biến." | "COD là viết tắt của thanh toán khi nhận hàng." | cao | 0.1303 | Không (dự đoán cao vì cùng nghĩa, thực tế lại thấp) |
| 4 | "Sản phẩm bị cấm không được phép đăng bán trên sàn." | "Mèo là loài động vật được nhiều người nuôi làm thú cưng." | thấp | 0.0378 | Đúng (gần 0) |
| 5 | "Tôi thích ăn phở vào buổi sáng." | "Tôi ghét ăn phở, không bao giờ ăn buổi sáng." | thấp (đối nghịch ý) | 0.0362 | Đúng theo hướng thấp, nhưng dự đoán ban đầu là "âm mạnh" thì sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 3: hai câu gần như đồng nghĩa 100% ("COD là gì" diễn giải lại chính nó) nhưng điểm chỉ 0.13, không hề cao như kỳ vọng. Điều này cho thấy `MockEmbedder` chỉ sinh vector từ hash MD5 của chuỗi ký tự — hoàn toàn không hiểu ngữ nghĩa, nên hai câu đồng nghĩa nhưng khác ký tự vẫn cho ra vector gần như ngẫu nhiên. Đây đúng là điều `exercises.md` đã cảnh báo: **không dùng mock embedder để kết luận về chất lượng ngữ nghĩa** — cần `EMBEDDING_PROVIDER=local` (hoặc embedder thật) để phép so sánh có ý nghĩa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

> Ghi chú: tại thời điểm nộp báo cáo cá nhân này, nhóm A6-1 **chưa hoàn tất crawl bộ tài liệu chính thức** (`data/k4_ecommerce/urls.csv` mới được chuẩn bị, chưa fetch) — 5 câu hỏi dưới đây được chạy tạm trên 2 tài liệu khởi động sẵn có (`k4-returns-policy`, `k4-seller-listing`) bằng `RecursiveChunker(chunk_size=300)` + `MockEmbedder`, sẽ cập nhật lại khi nhóm chốt bộ 5 câu hỏi chính thức trong `REPORT_NHOM.md`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người mua có bao nhiêu ngày để yêu cầu đổi trả hàng lỗi? | `k4-returns-policy`: "Người mua cần gửi yêu cầu đổi trả trong thời hạn được nêu trên trang sản phẩm…" | 0.2256 | Có (đúng doc_id, nhưng nội dung placeholder chưa nêu số ngày cụ thể) | Trả lời demo (chưa nối LLM thật) |
| 2 | Người bán cần cung cấp thông tin gì khi đăng bán sản phẩm? | `k4-seller-listing`: đoạn ghi chú metadata mẫu | 0.1141 | Một phần (đúng doc nhưng trúng vào đoạn metadata mẫu, không phải nội dung chính) | Trả lời demo (chưa nối LLM thật) |
| 3 | Sản phẩm nào không được phép đăng bán? | `k4-returns-policy`: "Người mua cần gửi yêu cầu đổi trả…" | 0.2340 | **Không** — lẽ ra phải trúng `k4-seller-listing` (nói về hàng cấm) nhưng lại trúng tài liệu đổi trả | Trả lời demo (chưa nối LLM thật) |
| 4 | Quy trình xử lý yêu cầu đổi trả của người bán là gì? | `k4-returns-policy` | 0.0615 | Có, nhưng score rất thấp | Trả lời demo (chưa nối LLM thật) |
| 5 | Chính sách đổi trả áp dụng cho vai trò người mua hay người bán? | `k4-returns-policy`: đoạn metadata mẫu | 0.1947 | Một phần | Trả lời demo (chưa nối LLM thật) |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5 (câu 3 lấy nhầm tài liệu do `MockEmbedder` không phân biệt ngữ nghĩa "đổi trả" và "hàng cấm").

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Sẽ bổ sung sau buổi demo giữa các nhóm; hiện tại bài học tự rút ra là: retrieval với mock embedder rất dễ trả kết quả sai lệch khi hai tài liệu dùng chung nhiều từ khóa hành chính giống nhau (ví dụ "người mua/người bán/sàn"), nên với dữ liệu tiếng Việt cần embedder ngữ nghĩa thật (`LocalEmbedder`) và/hoặc chiến lược chunking giữ nguyên heading/mục để tăng độ phân biệt giữa các tài liệu.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 (chưa chạy trên bộ tài liệu chính thức của nhóm) |
| **Tổng phần cá nhân** | **58 / 60** |
