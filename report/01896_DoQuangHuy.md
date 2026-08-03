# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đỗ Quang Huy — 2A202601896
**Nhóm:** BabyShark
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai đoạn văn bản có vector embedding "chỉ cùng hướng" trong không gian nhiều chiều — tức mô hình cho rằng chúng gần nhau về mặt ý nghĩa/chủ đề, dù cách diễn đạt (từ ngữ, thứ tự câu) có thể khác nhau hoàn toàn.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi thích ăn phở vào buổi sáng."
- Câu B: "Buổi sáng tôi hay ăn phở."
- Tại sao tương đồng: cùng nội dung (ăn phở, buổi sáng), chỉ khác thứ tự từ và cách diễn đạt — embedding nắm được ý nghĩa chứ không chỉ từ vựng nên hai câu này gần như "chỉ cùng hướng".

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi thích ăn phở vào buổi sáng."
- Câu B: "Giá cổ phiếu hôm nay giảm mạnh trên sàn giao dịch."
- Tại sao khác: hai câu nói về hai chủ đề hoàn toàn không liên quan (ẩm thực vs tài chính), không chia sẻ khái niệm ngữ nghĩa nào nên vector embedding chỉ theo hướng rất khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm đến **góc** (hướng) giữa hai vector, bỏ qua độ lớn (magnitude) — mà độ lớn của embedding thường bị ảnh hưởng bởi độ dài câu/tần suất từ chứ không phản ánh ý nghĩa. Euclidean distance lại nhạy với độ lớn này, nên hai câu cùng ý nghĩa nhưng độ dài khác nhau có thể bị tính là "xa nhau" dù về hướng (ý nghĩa) chúng gần như trùng nhau — vì vậy cosine đo đúng "mức độ giống nhau về ngữ nghĩa" hơn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> số chunk = làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11) = **23**
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap=100: số chunk = làm_tròn_lên((10000 - 100) / (500 - 100)) = làm_tròn_lên(9900 / 400) = làm_tròn_lên(24.75) = **25 chunks** (tăng thêm 2 chunk so với overlap=50). Mỗi bước trượt (chunk_size - overlap) nhỏ lại nên cần nhiều chunk hơn để phủ hết tài liệu. Ta muốn tăng overlap để giảm rủi ro một ý/câu quan trọng bị cắt đúng ngay ranh giới giữa hai chunk — phần chồng lặp giúp giữ ngữ cảnh liên tục, cải thiện chất lượng truy xuất, đổi lại là tốn thêm dung lượng lưu trữ và thời gian embedding do có nhiều chunk hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])\s+` (lookbehind sau dấu `.`, `!`, `?`, theo sau bởi khoảng trắng bất kỳ — bao gồm cả `\n`) để tách câu mà vẫn giữ dấu câu ở cuối mỗi câu. Sau khi tách, strip khoảng trắng và loại câu rỗng, rồi gom từng nhóm `max_sentences_per_chunk` câu nối lại bằng `" "`. Edge case: text rỗng trả về `[]`; nếu regex không tách được câu nào (không có dấu kết câu) thì toàn bộ text được coi là 1 "câu".

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt các separator theo độ ưu tiên (`\n\n` → `\n` → `. ` → ` ` → `""`). Nếu đoạn text hiện tại đã ≤ `chunk_size` thì trả về nguyên đoạn (base case). Nếu không, tách bằng separator đầu tiên rồi gộp dần các phần lại thành chunk chưa vượt `chunk_size`; phần nào tự nó vẫn quá lớn thì đệ quy `_split` tiếp với separator tiếp theo trong danh sách còn lại. Nếu hết separator (`remaining_separators` rỗng) thì cắt cứng theo `chunk_size` ký tự — đây là base case cuối cùng đảm bảo luôn dừng đệ quy.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được embed bằng `embedding_fn` và lưu thành 1 record (`id`, `content`, `metadata`, `embedding`) trong list `self._store` (in-memory) — metadata luôn được gán thêm `doc_id` mặc định bằng `doc.id` nếu chưa có, để phục vụ filter/xóa sau này. Khi `search`, câu truy vấn được embed rồi tính tích vô hướng (dot product) với embedding của từng record đã lưu (hàm `_dot`), sắp xếp giảm dần theo score và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata **trước** (chỉ giữ record mà mọi cặp key-value trong `metadata_filter` khớp), rồi mới chạy similarity search trên tập đã lọc — cách này tránh phải tính similarity trên toàn bộ store rồi mới bỏ. `delete_document` xóa bằng cách giữ lại các record có `metadata["doc_id"] != doc_id`, trả về `True` nếu kích thước store giảm sau khi lọc, ngược lại `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `__init__` lưu lại `store` và `llm_fn`. `answer` gọi `store.search(question, top_k)` để lấy các chunk liên quan, nối nội dung các chunk lại bằng `"\n\n"` làm phần "Ngữ cảnh", rồi ghép vào một prompt template gồm 3 phần: hướng dẫn trả lời dựa trên ngữ cảnh + ngữ cảnh + câu hỏi, cuối cùng gọi `llm_fn(prompt)` để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.09s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> **Embedder dùng:** OpenAI `text-embedding-3-small` (qua `OpenAIEmbedder`, đặt `EMBEDDING_PROVIDER=openai` trong `.env`) — không dùng mock vì mock chỉ sinh vector hash giả lập, không phản ánh ngữ nghĩa thật.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Chính sách đổi trả cho phép khách hàng hoàn trả sản phẩm trong vòng 30 ngày." | "Khách hàng có thể trả lại hàng trong 30 ngày kể từ ngày mua." | cao | 0.7813 | Đúng |
| 2 | "Người bán cần cung cấp thông tin gì khi đăng sản phẩm?" | "Điều kiện để người bán đăng bán sản phẩm trên sàn là gì?" | cao | 0.7243 | Đúng |
| 3 | "Thời gian giao hàng tiêu chuẩn là 3-5 ngày làm việc." | "Con mèo của tôi thích ngủ trên ghế sofa vào buổi chiều." | thấp | 0.2614 | Đúng |
| 4 | "Chính sách bảo mật quy định cách chúng tôi thu thập dữ liệu cá nhân." | "Phí vận chuyển được tính dựa trên khối lượng và khoảng cách." | thấp | 0.2908 | Đúng |
| 5 | "Đơn hàng đã thanh toán có được hủy không?" | "Tôi có thể hủy đơn hàng sau khi đã thanh toán không?" | cao | 0.8496 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **Cặp 4**: hai câu đều thuộc phạm trù "chính sách của sàn TMĐT" (bảo mật dữ liệu vs phí vận chuyển), nghe có vẻ "cùng chủ đề chính sách" hơn là hai câu hoàn toàn ngẫu nhiên — nhưng điểm số (0.29) gần như ngang với cặp hoàn toàn không liên quan ở Cặp 3 (0.26). Điều này cho thấy embedding nắm bắt **nội dung cụ thể** (quyền riêng tư dữ liệu vs phí giao hàng) chứ không phải nhãn chủ đề chung chung ("chính sách") — hai câu phải thực sự nói về cùng một khái niệm cụ thể thì mới được coi là tương đồng, chứ không chỉ vì cùng nằm trong một domain rộng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> Chiến lược dùng: `HeadingSectionChunker` (custom, chia theo heading `##`) — xem lý do chọn ở `REPORT_NHOM.md` Phần 2. Embedder: OpenAI `text-embedding-3-small`. Corpus: 5 tài liệu trong `data/k4_ecommerce/`. Chạy trực tiếp bằng `python bench.py --strategy heading_custom`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Giao sai kích cỡ/màu có được trả hàng không? | `k4-returns-policy` — "Điều kiện yêu cầu trả hàng/hoàn tiền" | 0.7013 | Có (đúng content) | Có — người bán giao sai sản phẩm (sai kích cỡ, màu sắc) là một điều kiện hợp lệ để yêu cầu trả hàng/hoàn tiền |
| 2 | Giao hàng hỏa tốc Lazada: khu vực & giới hạn khối lượng? | `k4-shipping-policy` — "2. Dịch vụ giao hàng hỏa tốc (4 giờ)" | 0.7179 | Có (đúng content) | Nội thành Hà Nội/TP.HCM, sản phẩm dưới 15kg và dưới 70cm, không áp dụng bỉm/tã |
| 3 | Nhà bán có được đăng hàng cũ trên Tiki không? *(lọc `customer_role=seller`)* | `k4-seller-listing` — "Hàng hóa cấm và hạn chế" | 0.5007 | Có (đúng content) | Không — Tiki không hỗ trợ đăng bán hàng cũ, đã qua sử dụng, like new, second hand |
| 4 | Giới hạn giá trị đơn hàng khi dùng Apple Pay? | `k4-payment-methods` — "7. Apple Pay" | 0.6931 | Có (đúng content) | Tối đa 25.000.000 VNĐ (phạm vi 10.000đ–25.000.000đ) |
| 5 | Sàn có chia sẻ dữ liệu cá nhân với chính phủ không? | `k4-privacy-policy` — "Loại dữ liệu cá nhân được thu thập" (top-1, chưa đúng mục) | 0.5668 | Có, nhưng ở **hạng 2** — chunk đúng ("Chia sẻ dữ liệu với bên thứ ba", score 0.5413) nằm ở top-2, không phải top-1 | Cần đọc cả 3 chunk top-3 mới thấy câu trả lời — nếu agent chỉ dùng top-1 sẽ trả lời thiếu; dùng cả top-3 thì có: "Có — khi được yêu cầu theo pháp luật" |

> Cột "Câu trả lời của Agent" là nội dung tóm tắt trực tiếp từ các chunk top-3 (chưa gọi LLM thật — mới chỉ dùng API embedding của OpenAI, chưa dùng API sinh văn bản). Câu 5 cho thấy rõ: dù cùng đúng tài liệu, thứ hạng của chunk chứa câu trả lời thật vẫn có thể lệch (hạng 2 thay vì hạng 1) — xem thêm phân tích lỗi (case tệ hơn với `RecursiveChunker`) ở `REPORT_NHOM.md` Phần 4.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (đúng tài liệu); 5/5 nếu tính "đúng content trong top-3" (câu 5 đúng content nhưng ở hạng 2, không phải hạng 1)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Chưa có — phần này cần buổi demo thật với các thành viên khác trong nhóm và các nhóm khác trong lớp, sẽ bổ sung sau khi demo.*

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
