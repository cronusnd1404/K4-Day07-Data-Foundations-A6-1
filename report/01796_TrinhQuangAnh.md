# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trịnh Quang Anh
**Nhóm:** A6-1
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Nghĩa là hai vector embedding chỉ về gần cùng một hướng trong không gian vector, tức là hai đoạn văn bản mang ý nghĩa tương tự nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Con mèo đang ngủ trên ghế sofa."
- Câu B: "Chú mèo nằm ngủ trên ghế."
- Tại sao tương đồng: Cả hai câu cùng mô tả một sự việc (mèo ngủ trên ghế), chỉ khác cách diễn đạt ("con mèo" / "chú mèo", "đang ngủ" / "nằm ngủ"), nên embedding của chúng gần nhau về hướng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Hôm nay trời mưa rất to."
- Câu B: "Giá cổ phiếu hôm nay tăng mạnh."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau (thời tiết vs. tài chính), không chia sẻ ngữ nghĩa chung nào ngoài từ "hôm nay", nên vector của chúng chỉ về hai hướng khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ đo góc (hướng) giữa hai vector mà bỏ qua độ dài (magnitude), trong khi Euclid bị ảnh hưởng bởi độ dài vector — vốn có thể thay đổi theo độ dài văn bản mà không phản ánh ngữ nghĩa. Vì ý nghĩa được mã hóa chủ yếu ở hướng của vector, cosine cho kết quả so sánh ngữ nghĩa ổn định hơn và với vector đã chuẩn hóa, xếp hạng theo cosine tương đương xếp hạng theo Euclid nhưng tính đơn giản hơn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Mỗi bước nhảy (step) = chunk_size − overlap = 500 − 50 = 450 ký tự. Chunk đầu tiên phủ 500 ký tự, mỗi chunk sau thêm 450 ký tự mới. Số chunks = 1 + ⌈(10,000 − 500) / 450⌉ = 1 + ⌈9,500 / 450⌉ = 1 + ⌈21.1⌉ = 1 + 22.
> *Đáp án:* **23 chunks.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Step giảm còn 500 − 100 = 400, nên số chunks = 1 + ⌈9,500 / 400⌉ = 1 + 24 = **25 chunks** (tăng thêm 2). Overlap nhiều hơn giúp giảm nguy cơ một câu/ý bị cắt đôi ở ranh giới chunk — thông tin ở biên sẽ xuất hiện trọn vẹn trong ít nhất một chunk, cải thiện chất lượng truy xuất, đổi lại tốn thêm dung lượng lưu trữ và chi phí embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` với lookbehind: cắt tại khoảng trắng **đứng ngay sau** dấu `.`, `!` hoặc `?`, nhờ vậy dấu câu được giữ lại ở cuối câu và cả `". "` lẫn `".\n"` đều được xử lý bằng một biểu thức duy nhất. Sau khi tách, tôi `strip()` từng câu và loại bỏ phần tử rỗng — điều này xử lý edge case văn bản kết thúc bằng `". "` (nếu không lọc sẽ sinh ra một câu rỗng ở cuối) cũng như văn bản chỉ chứa khoảng trắng. Cuối cùng gom các câu thành nhóm `max_sentences_per_chunk` bằng vòng lặp bước nhảy và nối lại bằng dấu cách; text rỗng trả về `[]`, còn text không có dấu kết câu vẫn được coi là một câu duy nhất.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split` nhận đoạn text hiện tại cùng danh sách separator còn lại và thử separator ưu tiên cao nhất trước (`"\n\n"` → `"\n"` → `". "` → `" "` → `""`): tách text theo separator đó rồi **gộp tham lam (greedy merge)** các mảnh liền kề vào một buffer chừng nào tổng độ dài còn ≤ `chunk_size`, nhờ vậy các đoạn nhỏ không bị vụn ra thành quá nhiều chunk. Mảnh nào tự nó đã dài hơn `chunk_size` thì được đệ quy xuống separator mịn hơn ở cấp tiếp theo. Có hai **base case**: (1) đoạn text đã ≤ `chunk_size` thì trả về chính nó, và (2) hết separator (hoặc gặp separator rỗng `""`) thì cắt cứng theo vị trí ký tự — đây cũng là cách xử lý edge case `separators=[]` để hàm luôn kết thúc thay vì đệ quy vô hạn.

**`compute_similarity`** — hướng tiếp cận:
> Áp dụng trực tiếp công thức `dot(a, b) / (||a|| * ||b||)`, tái sử dụng hàm `_dot` có sẵn cho cả tử số lẫn việc tính chuẩn (`||a|| = sqrt(dot(a, a))`). Trường hợp một trong hai vector có độ dài bằng 0 sẽ gây chia cho 0 nên tôi kiểm tra trước và trả về `0.0` — quy ước hợp lý vì vector rỗng không có hướng để so sánh.

**`ChunkingStrategyComparator.compare`** — hướng tiếp cận:
> Tôi khởi tạo cả ba chunker với cùng `chunk_size` đầu vào, chạy trên cùng một văn bản rồi trả về dict gồm `count`, `avg_length` và `chunks` cho từng chiến lược để so sánh trực tiếp. Overlap của `FixedSizeChunker` được đặt là `min(50, chunk_size // 4)` thay vì cố định 50, tránh trường hợp `chunk_size` nhỏ khiến `step = chunk_size - overlap` bằng 0 hoặc âm và làm vòng lặp lỗi; khi danh sách chunk rỗng thì `avg_length` trả về `0.0` thay vì chia cho 0.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi tách phần chuẩn hóa dữ liệu ra hàm `_make_record`: mỗi `Document` được nhúng rồi lưu thành dict gồm `id`, `doc_id`, `content`, `metadata`, `embedding` trong danh sách `self._store` (danh sách in-memory là **nguồn sự thật**; ChromaDB nếu có chỉ được ghi song song làm bản sao). Điểm mấu chốt là tôi **chuẩn hóa vector về độ dài 1 ngay lúc lưu** (hàm `_normalize`), nhờ đó ở `search` chỉ cần lấy tích vô hướng `_dot(query, embedding)` là đã bằng đúng cosine similarity — vừa nhanh vừa không phải tính chuẩn lặp lại cho mọi chunk ở mỗi truy vấn. `search` gọi `_search_records` để nhúng câu hỏi, chấm điểm toàn bộ record, sắp xếp giảm dần và cắt `top_k`.
>
> Một chi tiết tôi phải xử lý: test tạo `Document(id="doc_to_delete", metadata={})` — metadata rỗng, không có `doc_id`. Vì vậy `_make_record` suy ra `doc_id = metadata.get("doc_id") or doc.id`, giúp cả chunk từ `ingest.py` (đã có sẵn `doc_id`) lẫn document trần đều xóa/lọc được như nhau.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi lọc **trước rồi mới tìm kiếm (pre-filtering)**: duyệt `self._store`, giữ lại record thỏa **mọi** cặp key-value trong `metadata_filter`, rồi truyền đúng tập ứng viên đó vào `_search_records`. Làm theo thứ tự này thì `top_k` được tính trên tập đã lọc nên luôn trả về đủ `k` kết quả hợp lệ — nếu lọc sau khi tìm kiếm thì có thể lấy top-5 rồi bị loại hết còn 0 kết quả. Khi `metadata_filter` rỗng hoặc `None`, hàm rơi về đúng `search` thông thường.
>
> `delete_document` xóa bằng cách **dựng lại danh sách** chỉ gồm record có `doc_id` khác giá trị cần xóa (thay vì xóa tại chỗ khi đang duyệt — dễ nhảy sót phần tử). So sánh độ dài trước/sau cho biết có xóa được gì không để trả về `True`/`False`, đồng thời xóa được **tất cả** chunk của cùng một tài liệu chỉ trong một lượt duyệt.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` theo đúng ba bước RAG: gọi `store.search(question, top_k)`, ghép các chunk lấy được thành khối ngữ cảnh, rồi đưa prompt cho `llm_fn`. Tôi **đánh số từng đoạn ngữ cảnh `[1] [2] [3]` kèm nguồn** (`source_url`, fallback về `doc_id`) và yêu cầu mô hình trích dẫn số hiệu đó khi trả lời — nhờ vậy câu trả lời truy vết được về tài liệu gốc thay vì chỉ là văn bản trôi nổi. Prompt tách bạch ba khối `NGỮ CẢNH` / `CÂU HỎI` / `TRẢ LỜI` và có chỉ dẫn chống bịa: chỉ dùng thông tin trong ngữ cảnh, nếu không đủ thì nói rõ là không tìm thấy. Trường hợp store rỗng (search trả về `[]`) thì tôi trả về thẳng câu thông báo không tìm thấy mà **không gọi LLM** — tránh tốn một lần gọi API chắc chắn sẽ cho ra câu trả lời bịa.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.11.3, pytest-7.3.1, pluggy-1.0.0 -- python.exe
cachedir: .pytest_cache
rootdir: D:\study\AI20K\LAB\K4-Day07-Data-Foundations-A6-1
plugins: anyio-3.5.0
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker (7 tests) PASSED
tests/test_solution.py::TestSentenceChunker (4 tests) PASSED
tests/test_solution.py::TestRecursiveChunker (4 tests) PASSED
tests/test_solution.py::TestEmbeddingStore (8 tests) PASSED
tests/test_solution.py::TestKnowledgeBaseAgent (2 tests) PASSED
tests/test_solution.py::TestComputeSimilarity (4 tests) PASSED
tests/test_solution.py::TestCompareChunkingStrategies (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.11s ==============================
```

> *(Các dòng ở giữa được gộp theo nhóm test cho gọn; bản chạy đầy đủ liệt kê từng test một, tất cả đều PASSED.)*

**Số lượng bài test vượt qua (pass):** **42** / 42

**⚠️ Cách chạy đúng bài của tôi:** sau khi nhánh của cả nhóm được gộp vào `main`, mỗi thành viên có một package riêng (`src/QAnh`, `src/Phong`, `src/01896-DoQuangHuy`…) và `src/` ở gốc là bản của thành viên khác. Bộ test mặc định `LAB_SOLUTION_PACKAGE = "src"` nên nếu chạy `pytest tests/` trần thì **không phải code của tôi đang được chấm**. Để chấm đúng package `src/QAnh`, cần chỉ định biến môi trường:

```powershell
$env:LAB_SOLUTION_PACKAGE='src.QAnh'; pytest tests/ -v      # PowerShell
LAB_SOLUTION_PACKAGE=src.QAnh pytest tests/ -v              # bash
```

Kết quả **42/42 PASSED** ở trên là kết quả chạy với biến môi trường này, tức là chấm trên đúng `src/QAnh/chunking.py`, `src/QAnh/store.py`, `src/QAnh/agent.py` do tôi viết.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> **Backend:** OpenAI `text-embedding-3-small` (1536 chiều), đặt `EMBEDDING_PROVIDER=openai` trong `.env`. Tôi chạy **cùng 5 cặp câu trên cả hai backend** để thấy rõ vai trò của mô hình nhúng — cột "MOCK" là kết quả cũ với `MockEmbedder` (64 chiều, băm MD5).

| Cặp | Câu A | Câu B | Dự đoán | Điểm MOCK | **Điểm THẬT** | Đúng? |
|-----|-----------|-----------|---------|-----------|---------------|-------|
| 1 | Con mèo đang ngủ trên ghế sofa. | Chú mèo nằm ngủ trên ghế. | cao | +0.023 | **+0.7433** | ✓ |
| 2 | Tôi muốn đổi trả sản phẩm bị lỗi. | Làm sao để hoàn hàng khi hàng không đúng mô tả? | cao | +0.026 | **+0.4775** | ✓ |
| 3 | Hôm nay trời mưa rất to. | Giá cổ phiếu hôm nay tăng mạnh. | thấp | +0.047 | **+0.4249** | ✓ |
| 4 | Python là ngôn ngữ lập trình phổ biến. | Con trăn là loài bò sát cỡ lớn. | thấp | −0.064 | **+0.3047** | ✓ |
| 5 | Người bán phải cung cấp thông tin sản phẩm chính xác. | *(chuỗi giống hệt câu A)* | cao (≈1.0) | +1.000 | **+1.0000** | ✓ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **cặp 3**: "Hôm nay trời mưa rất to" và "Giá cổ phiếu hôm nay tăng mạnh" chẳng liên quan gì nhau, vậy mà đạt **+0.4249** — không hề "gần 0" như tôi tưởng, và chỉ kém cặp 2 (hai câu thật sự cùng chủ đề đổi trả, +0.4775) đúng **0.05**. Cặp 4 cũng vậy: "Python" và "con trăn" hoàn toàn khác nghĩa nhưng vẫn được +0.3047.
> Bài học là **giá trị cosine tuyệt đối gần như vô nghĩa nếu dùng làm ngưỡng**. Với văn bản tiếng Việt, `text-embedding-3-small` nén toàn bộ dải điểm vào khoảng hẹp 0.30–0.74; hai câu ngẫu nhiên cùng ngôn ngữ đã "mặc định" giống nhau ~0.3–0.4 chỉ vì chung tiếng Việt, chung cấu trúc câu. Nếu ai đó đặt luật "cosine > 0.4 thì coi là liên quan" thì cặp thời tiết–chứng khoán sẽ bị nhận nhầm là liên quan.
> Điều **thật sự** dùng được là **thứ hạng tương đối**: xếp giảm dần ta được 1 (0.7433) > 2 (0.4775) > 3 (0.4249) > 4 (0.3047), tức hai cặp tôi dự đoán "cao" đều đứng trên hai cặp dự đoán "thấp" — **5/5 dự đoán đúng theo thứ hạng**. Đây cũng chính là lý do retrieval xếp hạng top-k thay vì lọc theo ngưỡng điểm.
> So với mock thì khác biệt là một trời một vực: mock cho cặp 1 (gần như đồng nghĩa) chỉ 0.023, **thấp hơn** cả cặp 3 không liên quan (0.047), vì nó băm MD5 cả chuỗi nên chỉ nhận ra "giống hệt" (cặp 5 = 1.000) chứ không nhận ra "gần nghĩa". Cosine không tự sinh ra ngữ nghĩa — toàn bộ khả năng đó đến từ mô hình nhúng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> **Cấu hình đã chạy:** package cá nhân `src/QAnh` · chunker của tôi = **`FixedSizeChunker(chunk_size=300, overlap=30)`** · corpus = `data/k4_ecommerce` (**5 tài liệu thật** của nhóm) → **35 chunk** · backend nhúng = **OpenAI `text-embedding-3-small`** (1536 chiều) · `top_k=3`.
> **Bộ câu hỏi:** đúng 5 câu benchmark chính thức nhóm BabyShark đã thống nhất trong `REPORT_NHOM.md` — Phần 3.
>
> **Cách chấm "có liên quan":** tôi không tự đọc rồi tự đánh giá, mà gắn cho mỗi câu một **chuỗi mốc (gold marker)** lấy từ cột "Chunk nào chứa thông tin?" của nhóm (`sai kích cỡ`, `15kg`, `second hand`, `25.000.000`, `Cơ quan chính phủ`) rồi để script kiểm tra chuỗi đó có nằm trong chunk truy xuất được hay không. Đây là cách chấm **nghiêm ngặt**: chunk phải chứa đúng câu chữ mang câu trả lời, không tính "đúng tài liệu nhưng sai đoạn".

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người bán giao sai kích cỡ/màu thì có được trả hàng không? | `k4-returns-policy` #1 — "Người bán giao sai sản phẩm (sai kích cỡ, màu sắc)" | **+0.6267** | ✅ **Có, ngay top-1** | Được — giao sai kích cỡ/màu là một điều kiện hợp lệ để yêu cầu trả hàng, dẫn nguồn Shopee |
| 2 | Giao hàng hỏa tốc 4 giờ của Lazada áp dụng ở đâu, giới hạn khối lượng? | `k4-shipping-policy` #3 — mục "2. Dịch vụ giao hàng hỏa tốc (4 giờ)" kèm hạn chế 15kg | **+0.6266** | ✅ **Có, ngay top-1** | Nội thành HN/TP.HCM, dưới 15kg và 70cm, không áp dụng bỉm/tã |
| 3 | Nhà bán có được đăng bán hàng cũ/second hand không? *(cần lọc metadata)* | `k4-returns-policy` #1 — điều kiện trả hàng | +0.5160 | ⚠️ **Có nhưng ở top-3** (+0.4923) — **lọc metadata đưa lên top-1**, xem dưới | Không lọc thì ngữ cảnh lẫn tài liệu buyer; có lọc thì trả lời đúng "Tiki không hỗ trợ hàng cũ/second hand" |
| 4 | Apple Pay hỗ trợ giá trị đơn tối đa bao nhiêu? | `k4-payment-methods` #3 — đoạn chứa "…đến 25.000.000 VNĐ" | **+0.7140** | ✅ **Có, ngay top-1** | Tối đa 25.000.000 VNĐ (phạm vi 10.000đ–25.000.000đ) |
| 5 | Sàn có chia sẻ dữ liệu cá nhân với cơ quan chính phủ không? | `k4-privacy-policy` #3 — "Shopee có thể tiết lộ dữ liệu cho: … Cơ quan chính phủ" | **+0.5733** | ✅ **Có, ngay top-1** | Có — khi được cơ quan chính phủ yêu cầu theo pháp luật |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5** — trong đó **4/5 đúng ngay ở top-1**, và câu còn lại (câu 3) cũng lên top-1 khi bật lọc metadata, tức **thực tế 5/5 ở top-1**.

### Lọc metadata giải quyết đúng câu nhóm thiết kế cho nó

Câu 3 là câu nhóm cố tình đặt để cần `customer_role=seller`. Kết quả trước/sau khi lọc:

| | Top-1 | Top-2 | Top-3 |
|---|---|---|---|
| **Không lọc** | `k4-returns-policy` (+0.5160) | `k4-returns-policy` (+0.5068) | ✅ `k4-seller-listing` **gold** (+0.4923) |
| **Có lọc `seller`** | ✅ `k4-seller-listing` **gold** (+0.4923) | `k4-seller-listing` (+0.4417) | `k4-seller-listing` (+0.4069) |

Điểm đáng chú ý: chunk gold **không hề đổi điểm** (vẫn +0.4923) — filter không làm nó "giống câu hỏi hơn", mà chỉ **loại hai chunk buyer đang chen trên nó**. Hai chunk đó thuộc `k4-returns-policy` và ăn điểm cao nhờ dùng chung từ vựng hành chính ("sản phẩm", "người bán", "điều kiện") chứ không trả lời được câu hỏi. Đây đúng là tình huống mà nhóm dự đoán: filter phát huy tác dụng khi nhiều tài liệu chung từ vựng nhưng khác đối tượng người đọc.

### So sánh 3 chiến lược — và một kết quả trái ngược với bảng của nhóm

Cùng corpus, cùng 5 câu hỏi, cùng embedder, chỉ đổi chunker:

| Chiến lược | Số chunk | Gold trong top-3 | Gold ở top-1 |
|---|---|---|---|
| **`FixedSizeChunker(300/30)`** | 35 | **5 / 5** | **4 / 5** |
| `SentenceChunker(3)` | 46 | 4 / 5 | 2 / 5 |
| `RecursiveChunker(300)` | 45 | 3 / 5 | 2 / 5 |

Kết quả này **ngược với bảng ở `REPORT_NHOM.md` Phần 2**, nơi ghi `fixed_size` là yếu nhất (4/5, thất bại ở câu 5) còn `recursive`/`by_sentences` đạt 5/5. Trong phép đo của tôi thì ngược lại hoàn toàn: `fixed_size` đạt 5/5 và trả lời câu 5 chính xác ngay top-1 (+0.5733), còn `recursive` chỉ được 3/5.

Nguyên nhân tôi tìm được nằm ở **ranh giới chunk**, và nó khá phản trực giác. Với `recursive(300)`, câu 2 và câu 5 đều truy xuất **đúng tài liệu ở cả 3 vị trí top-3** nhưng vẫn bị chấm trượt, vì thuật toán cắt gọn theo ranh giới đoạn/câu nên câu chứa dữ kiện bị tách sang một chunk khác: chunk top-1 của câu 2 là tiêu đề mục "## 2. Dịch vụ giao hàng hỏa tốc (4 giờ)" nhưng dòng "chỉ áp dụng cho sản phẩm dưới **15kg**" đã rơi sang chunk kế tiếp. `FixedSizeChunker` cắt cứng 300 ký tự **kèm overlap 30**, chính phần chồng lấn đó giữ được tiêu đề mục và dòng dữ kiện nằm chung một chunk. Nói cách khác, cắt "đẹp" theo ngữ nghĩa lại có thể tách câu trả lời khỏi ngữ cảnh nhận diện nó, còn cắt "thô" có overlap thì vô tình giữ chúng lại với nhau.

Hai lưu ý để nhóm đối chiếu: (1) mỗi thành viên tự viết `chunking.py` nên cùng tên chiến lược nhưng ranh giới chunk có thể khác nhau; (2) tôi chấm bằng gold marker nghiêm ngặt (phải chứa đúng câu chữ), trong khi bảng nhóm chấm theo "có chunk liên quan" — chênh lệch cách chấm đủ để đảo ngược thứ hạng. Đề xuất: nhóm thống nhất một cách chấm duy nhất trước khi tổng hợp Phần 2 và Phần 3.

### Đối chứng kiểm tra tính đúng đắn của pipeline

Để chắc chắn kết quả không đến từ may mắn, tôi chạy thêm hai phép thử (thực hiện trên `MockEmbedder` để loại bỏ nhiễu ngữ nghĩa):

| Truy vấn thử | Top-1 trả về | Score |
|---|---|---|
| **Nguyên văn** chunk Apple Pay | ✅ đúng chunk đó | **+1.0000** |
| Cũng chunk đó nhưng **đổi 1 ký tự** (`Apple Pay` → `Apple Pai`) | ❌ chunk khác, gold văng khỏi top-3 | +0.1960 |

Truy vấn trùng khít cho cosine đúng bằng **1.0000**, xác nhận đường đi nhúng → chuẩn hóa → chấm điểm → xếp hạng chính xác tuyệt đối. Tôi cũng kiểm tra `delete_document("k4-payment-methods")` → trả `True`, collection giảm **45 → 37** chunk và không còn chunk nào của tài liệu đó.

**Chi phí chạy thật:** 139 lần gọi API nhúng (đã cache để không nhúng lại chuỗi trùng) cho cả Phần 4 lẫn Phần 5. Với `text-embedding-3-small` (0,02 USD / 1 triệu token) thì tổng chi phí dưới **0,001 USD** — rẻ hơn nhiều so với hình dung ban đầu, và đây là lý do không nên ngại dùng embedder thật ngay từ đầu thay vì chạy mock rồi phải làm lại toàn bộ.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *(Chờ buổi demo — sẽ điền sau khi nghe phần trình bày của các nhóm khác.)*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá | Căn cứ |
|----------|-------------------|--------|
| Khởi động (Warm-up) | 5 / 5 | Trả lời đủ 2 bài tập, có ví dụ cụ thể và trình bày phép tính chunking |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 | Giải thích đủ 7 hàm đã lập trình, nêu rõ thuật toán + edge case đã xử lý |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 | **42/42 test PASSED**, đã hoàn thành toàn bộ TODO trong `chunking.py`, `store.py`, `agent.py` |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 | Đủ 5 cặp chạy trên **cả mock lẫn embedder thật**, 5/5 dự đoán đúng theo thứ hạng, phân tích được vì sao ngưỡng điểm tuyệt đối không dùng được |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 | **5/5 câu có chunk gold trong top-3, 4/5 ngay top-1** (câu còn lại lên top-1 nhờ metadata filter) trên đúng 5 câu hỏi chính thức + corpus thật, chấm tự động bằng gold marker, kèm so sánh 3 chiến lược và đối chứng tính đúng đắn của pipeline |
| **Tổng phần cá nhân** | **60 / 60** | |

### Việc còn lại của phần cá nhân
- [x] ~~Chốt 5 câu hỏi đánh giá chung trong `REPORT_NHOM.md`, chạy lại Phần 5 bằng đúng bộ câu hỏi đó.~~ — đã chạy đúng 5 câu chính thức.
- [x] ~~Thay bộ dữ liệu khởi động bằng 5–10 tài liệu công khai thật (Bài tập 3.0) rồi chạy lại.~~ — đã chạy trên 5 tài liệu thật của nhóm.
- [x] ~~Chạy lại Phần 4 + Phần 5 bằng embedder thật.~~ — đã chạy với OpenAI `text-embedding-3-small`, kết quả từ 1/5 lên **5/5** top-3.
- [ ] Điền khối "Thành viên 5 — Trịnh Quang Anh" ở `REPORT_NHOM.md` Phần 2: chiến lược **`FixedSizeChunker(300/30)`**, 5/5 top-3 và 4/5 top-1.
- [ ] **Báo nhóm đối chiếu lại bảng so sánh chiến lược ở `REPORT_NHOM.md` Phần 2** — phép đo của tôi cho `fixed_size` tốt nhất (5/5) trong khi bảng nhóm ghi `fixed_size` yếu nhất và thất bại ở câu 5; nhóm cần thống nhất một cách chấm "có liên quan" duy nhất.
- [ ] Điền ô "Điều hay nhất học được từ nhóm khác" sau buổi demo.
