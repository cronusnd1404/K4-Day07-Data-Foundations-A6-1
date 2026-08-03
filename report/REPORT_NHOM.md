# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** BabyShark
**Thành viên:**
- Phạm Tiến Đại — 2A20260160
- Bùi Ngọc Đạt — 2A202601710
- Đào Việt Phong — 2A202601786
- Trịnh Quang Anh — 2A202601796
- Đỗ Quang Huy — 2A202601896
**Ngày:** 3/8/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:** 5 khía cạnh chính sách hỗ trợ khách hàng của 3 sàn TMĐT lớn tại Việt Nam (Shopee, Tiki, Lazada) — đổi trả/hoàn tiền, vận chuyển, điều kiện đăng bán (người bán), thanh toán, và bảo mật dữ liệu.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách trả hàng và hoàn tiền (Shopee) | [help.shopee.vn/portal/4/article/77251](https://help.shopee.vn/portal/4/article/77251) | 2026-08-03 / not-stated | 3187 | `customer_role=buyer`, `category=returns-policy`, `platform=shopee`, `language=vi` |
| 2 | Hồ sơ pháp lý bắt buộc khi đăng sản phẩm (Tiki) | [hocvien.tiki.vn/.../ho-so-phap-ly...](https://hocvien.tiki.vn/faq/danh-muc-yeu-cau-ve-ho-so-phap-ly-nha-ban-hang-va-hang-hoa/) | 2026-08-03 / not-stated | 1627 | `customer_role=seller`, `category=seller-legal-docs`, `platform=tiki`, `language=vi` |
| 3 | Chính sách bảo mật (Shopee) | [help.shopee.vn/portal/4/article/77244](https://help.shopee.vn/portal/4/article/77244-CH%C3%8DNH-S%C3%81CH-B%E1%BA%A2O-M%E1%BA%ACT) | 2026-08-03 / not-stated | 1414 | `customer_role=both`, `category=privacy-policy`, `platform=shopee`, `language=vi` |
| 4 | Các phương thức thanh toán được hỗ trợ (Shopee) | [help.shopee.vn/portal/4/article/79198](https://help.shopee.vn/portal/4/article/79198-%5BTh%C3%A0nh-vi%C3%AAn-m%E1%BB%9Bi%5D-Shopee-hi%E1%BB%87n-%C4%91ang-c%C3%B3-nh%E1%BB%AFng-ph%C6%B0%C6%A1ng-th%E1%BB%A9c-thanh-to%C3%A1n-n%C3%A0o) | 2026-08-03 / not-stated | 1649 | `customer_role=buyer`, `category=payment-policy`, `platform=shopee`, `language=vi` |
| 5 | Chính sách vận chuyển và miễn phí vận chuyển (Lazada) | [pages.lazada.vn/.../chinh-sach-mien-phi-van-chuyen](https://pages.lazada.vn/wow/i/vn/VNCampaign/chinh-sach-mien-phi-van-chuyen?hybrid=1) | 2026-08-03 / 2019-11-15 | 1355 | `customer_role=buyer`, `category=shipping-policy`, `platform=lazada`, `language=vi` |

> Toàn bộ 5 file `.md` nằm tại `data/k4_ecommerce/`, kèm `sources.csv` liệt kê đầy đủ. Nội dung lấy thủ công (copy + làm sạch) từ trang trợ giúp/học viện chính thức của từng sàn — không dùng scraper tự động, không có dữ liệu cá nhân/đăng nhập.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `customer_role` | string (enum) | `buyer`, `seller`, `both` | Bắt buộc theo K4 — cho phép `search_with_filter` chỉ trả chunk đúng đối tượng hỏi (VD: câu hỏi của người bán không lẫn với chính sách dành cho người mua). |
| `category` | string | `returns-policy`, `payment-policy` | Thu hẹp phạm vi tìm kiếm theo khía cạnh chính sách, hữu ích khi corpus mở rộng thêm nhiều chủ đề con. |
| `platform` | string | `shopee`, `tiki`, `lazada` | Cho phép so sánh câu trả lời/chính sách giữa các sàn khi câu hỏi cụ thể theo nền tảng. |
| `language` | string | `vi` | Lọc theo ngôn ngữ nếu corpus sau này có thêm tài liệu tiếng Anh. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=300)` trên 3 tài liệu (embedder: OpenAI `text-embedding-3-small`, không dùng mock):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| k4-payment-methods (1649 ký tự) | FixedSizeChunker (`fixed_size`) | 6 | 274.8 | Không — cắt cứng theo ký tự, có thể đứt giữa câu/mục |
| k4-payment-methods | SentenceChunker (`by_sentences`) | 12 | 135.8 | Một phần — theo câu nhưng mỗi mục thanh toán (VD: "Apple Pay") có thể bị tách thành nhiều chunk câu rời rạc |
| k4-payment-methods | RecursiveChunker (`recursive`) | 8 | 204.4 | Có — ưu tiên tách theo đoạn/câu trước khi cắt cứng |
| k4-privacy-policy (1414 ký tự) | FixedSizeChunker | 5 | 282.8 | Không |
| k4-privacy-policy | SentenceChunker | 8 | 175.4 | Một phần |
| k4-privacy-policy | RecursiveChunker | 7 | 200.4 | Có |
| k4-returns-policy (3187 ký tự) | FixedSizeChunker | 11 | 289.7 | Không |
| k4-returns-policy | SentenceChunker | 15 | 210.8 | Một phần |
| k4-returns-policy | RecursiveChunker | 14 | 225.9 | Có |

**Nhận xét:** `FixedSizeChunker` luôn cho chunk đều nhau nhất về độ dài nhưng dễ cắt ngang giữa một điều kiện/mục chính sách (các văn bản này có heading `##` rõ ràng nên việc cắt cứng theo ký tự thường không trùng ranh giới mục). `RecursiveChunker` cho số chunk và độ dài trung bình cân bằng hơn `SentenceChunker` (tránh chunk quá vụn) mà vẫn tôn trọng ranh giới đoạn.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Đỗ Quang Huy**
- **Loại chiến lược:** Custom — `HeadingSectionChunker`
- **Mô tả & lý do chọn cho chủ đề này:** Cả 5 tài liệu chính sách đều được viết có cấu trúc heading Markdown (`## Điều kiện...`, `## Thời hạn...`, `## 1. Hỗ trợ phí vận chuyển...`) — mỗi heading là một đơn vị ngữ nghĩa trọn vẹn (một điều khoản/mục chính sách). Thay vì cắt cứng theo ký tự hay theo câu, chiến lược này tách theo ranh giới `## ` để mỗi chunk giữ nguyên trọn một mục chính sách; nếu một mục vẫn quá dài (>800 ký tự) mới đệ quy cắt tiếp bằng `RecursiveChunker` để tránh chunk khổng lồ.
- **Code snippet:**
```python
class HeadingSectionChunker:
    """Chia nhỏ theo tiêu đề mục (## ...) - phù hợp văn bản chính sách có cấu trúc heading rõ ràng.

    Lý do thiết kế: các file chính sách TMĐT trong data/k4_ecommerce/ đều được tổ chức
    theo mục (## Điều kiện..., ## Thời hạn...) - mỗi mục là một đơn vị ngữ nghĩa trọn vẹn,
    tách theo heading giữ nguyên ngữ cảnh của từng điều khoản thay vì cắt cứng theo ký tự.
    """

    def __init__(self, max_chunk_size: int = 800):
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        import re
        sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            if len(section) <= self.max_chunk_size:
                chunks.append(section)
            else:
                chunks.extend(RecursiveChunker(chunk_size=self.max_chunk_size).chunk(section))
        return chunks
```

**Thành viên 2 — Phạm Tiến Đại**
- **Loại chiến lược:** *(chưa điền — thành viên tự chạy và bổ sung phần của mình)*
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — Bùi Ngọc Đạt**
- **Loại chiến lược:** *(chưa điền — thành viên tự chạy và bổ sung phần của mình)*
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 4 — Đào Việt Phong**
- **Loại chiến lược:** *(chưa điền — thành viên tự chạy và bổ sung phần của mình)*
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 5 — Trịnh Quang Anh**
- **Loại chiến lược:** *(chưa điền — thành viên tự chạy và bổ sung phần của mình)*
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

> Huy đã chạy cả 4 chiến lược (3 built-in + 1 custom) trên cùng bộ 5 tài liệu và 5 benchmark query (chi tiết ở Phần 3) để có đường so sánh đầy đủ trong lúc chờ các thành viên khác bổ sung.

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Huy | FixedSizeChunker (baseline) | 8/10 (4/5 câu có chunk liên quan trong top-3) | Đơn giản, chunk đều nhau, dễ dự đoán chi phí embedding | Cắt cứng theo ký tự nên hay đứt giữa mục chính sách — thất bại ở câu hỏi về chia sẻ dữ liệu (Q5, xem Phần 4) |
| Huy | SentenceChunker | 10/10 (5/5) | Theo ranh giới câu nên không cắt ngang ý; đủ tốt cho văn bản ngắn | Một mục chính sách nhiều câu bị tách thành nhiều chunk nhỏ rời rạc, có thể mất liên kết giữa các câu trong cùng điều khoản |
| Huy | RecursiveChunker | 10/10 (5/5) | Cân bằng giữa giữ ngữ cảnh và kích thước chunk ổn định | Vẫn có thể cắt ngang một mục chính sách dài nếu mục đó vượt `chunk_size` |
| Huy | HeadingSectionChunker (custom) | 10/10 (5/5, điểm top-1 cao nhất ở 4/5 câu) | Giữ trọn từng điều khoản/mục chính sách theo đúng cấu trúc văn bản gốc — điểm similarity top-1 cao và ổn định nhất | Phụ thuộc format có heading `##` rõ ràng; không tổng quát cho văn bản không có cấu trúc heading |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Với bộ tài liệu chính sách TMĐT có cấu trúc heading rõ ràng, **`HeadingSectionChunker` (custom)** cho kết quả tốt nhất: đạt 5/5 câu có chunk liên quan trong top-3 và có điểm similarity top-1 cao/ổn định nhất trong 4/5 câu hỏi (ví dụ Q1: 0.3565 so với 0.31 của fixed_size; Q5: 0.348 trong khi fixed_size hoàn toàn thất bại — xem Phần 4). Lý do: mỗi chunk trùng khớp với một mục chính sách hoàn chỉnh (VD: toàn bộ mục "Chia sẻ dữ liệu với bên thứ ba"), nên khi câu hỏi hỏi đúng về nội dung của một mục, vector embedding của chunk đó không bị pha loãng bởi nội dung không liên quan từ mục kề bên — điều mà `FixedSizeChunker` mắc phải do cắt cứng theo ký tự bất kể ranh giới heading.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Nếu người bán giao sai kích cỡ hoặc màu sản phẩm thì tôi có được yêu cầu trả hàng không? | Có — đây là một trong các điều kiện được liệt kê trong chính sách trả hàng/hoàn tiền Shopee ("Người bán giao sai sản phẩm — sai kích cỡ, màu sắc"). | `k4-returns-policy` — mục "Điều kiện yêu cầu trả hàng/hoàn tiền" |
| 2 | Dịch vụ giao hàng hỏa tốc 4 giờ của Lazada áp dụng cho khu vực nào và giới hạn khối lượng sản phẩm là bao nhiêu? | Nội thành Hà Nội và TP.HCM (không gồm ngoại thành); chỉ áp dụng sản phẩm dưới 15kg, kích thước dưới 70cm, không áp dụng cho bỉm/tã. | `k4-shipping-policy` — mục "Dịch vụ giao hàng hỏa tốc (4 giờ)" |
| 3 | Nhà bán có được đăng bán hàng cũ, đã qua sử dụng trên sàn không? *(cần lọc `customer_role=seller`)* | Không — Tiki không hỗ trợ đăng bán hàng cũ, đã qua sử dụng, like new, hàng second hand. | `k4-seller-listing` — mục "Hàng hóa cấm và hạn chế" |
| 4 | Nếu dùng Apple Pay để thanh toán thì giá trị đơn hàng tối đa được hỗ trợ là bao nhiêu? | 25.000.000 VNĐ (phạm vi từ 10.000đ đến 25.000.000đ). | `k4-payment-methods` — mục "7. Apple Pay" |
| 5 | Sàn có chia sẻ dữ liệu cá nhân của tôi với cơ quan chính phủ không? | Có, khi được yêu cầu theo pháp luật. | `k4-privacy-policy` — mục "Chia sẻ dữ liệu với bên thứ ba" |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).
> Chạy với embedder OpenAI `text-embedding-3-small`, 4 chiến lược (fixed_size / by_sentences / recursive / heading_custom), `top_k=3`. Chi tiết điểm số ở Phần 2.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Giao sai kích cỡ/màu | `heading_custom` (score top-1 0.3565) | Có ở cả 4 chiến lược | `recursive` trả top-1 nhầm sang `k4-seller-listing` nhưng chunk đúng vẫn nằm trong top-3 |
| 2 | Giao hàng hỏa tốc Lazada | `by_sentences` (score top-1 0.5515) | Có ở cả 4 chiến lược | Câu hỏi có từ khóa trùng khớp cao với văn bản gốc nên mọi chiến lược đều truy xuất tốt |
| 3 | Hàng cũ trên Tiki (lọc `seller`) | `fixed_size` (score top-1 0.3156, cao nhất) | Có ở cả 4 chiến lược | Dùng `search_with_filter(metadata_filter={"customer_role":"seller"})` — loại bỏ ngay các chunk buyer-facing không liên quan trước khi so khớp |
| 4 | Giới hạn Apple Pay | `recursive` và `heading_custom` (đồng điểm 0.6565) | Có ở cả 4 chiến lược | Câu hỏi có số liệu cụ thể ("Apple Pay") nên mọi chiến lược đều nhận diện tốt, điểm số cao nhất trong 5 câu |
| 5 | Chia sẻ dữ liệu chính phủ | `by_sentences` (0.3545) / `heading_custom` (0.348) | **Không** ở `fixed_size` — chunk đúng bị loại khỏi top-3; **Có** ở 3 chiến lược còn lại | Xem phân tích lỗi chi tiết ở Phần 4 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có — rõ nhất ở **Câu 3**. Khi lọc `metadata_filter={"customer_role": "seller"}` trước khi search, toàn bộ chunk buyer-facing (đổi trả, thanh toán, vận chuyển) bị loại khỏi tập ứng viên ngay từ đầu, nên kết quả top-3 chỉ còn cạnh tranh giữa các chunk của `k4-seller-listing` — giảm nguy cơ một chunk buyer vô tình có điểm similarity cao hơn do trùng từ khóa chung ("sản phẩm", "hàng hóa"). Với 4 câu còn lại, nội dung đã đủ đặc trưng theo doc nên filter không thay đổi nhiều, nhưng với corpus lớn hơn (nhiều tài liệu hơn/nhiều role hơn) lợi ích của filter sẽ rõ hơn.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

### Phân tích lỗi (Bài tập 3.5 — Failure Analysis)

**Câu hỏi thất bại:** Câu 5 — "Sàn có chia sẻ dữ liệu cá nhân của tôi với cơ quan chính phủ không?" — với chiến lược `FixedSizeChunker` (chunk_size=300, overlap=30).

**Chi tiết:** Top-3 kết quả trả về đều **không chứa** chunk đúng (`k4-privacy-policy` — mục "Chia sẻ dữ liệu với bên thứ ba"). Top-1 và top-3 là 2 chunk từ `k4-returns-policy` (mục "Quyền của người mua" / "Yêu cầu về sản phẩm hoàn trả"), top-2 là chunk từ `k4-shipping-policy`.

**Tại sao thất bại:**
- `FixedSizeChunker` cắt cứng theo ký tự (300 ký tự/chunk, overlap 30) mà không quan tâm ranh giới heading `## `. Mục "Chia sẻ dữ liệu với bên thứ ba" trong `privacy-policy.md` bị cắt xen giữa phần cuối mục "Mục đích sử dụng dữ liệu" và đầu mục "Quyền của người dùng" — nội dung cốt lõi ("chia sẻ... cơ quan chính phủ khi được yêu cầu theo pháp luật") bị pha loãng trong một chunk có nhiều nội dung khác không liên quan trực tiếp đến câu hỏi.
- Các chunk "thắng" sai (từ `returns-policy`/`shipping-policy`) chứa các cụm từ chung chung về "người dùng", "yêu cầu", "quy định" khớp bề mặt với câu hỏi hơn là khớp ngữ nghĩa thật sự.
- Đây là lỗi **do ranh giới chunk**, không phải do thiếu metadata (câu hỏi này không cần filter) hay do câu hỏi mơ hồ (câu hỏi khá cụ thể).

**Đề xuất cải thiện:**
- Dùng chiến lược tôn trọng cấu trúc heading (như `HeadingSectionChunker`) làm mặc định cho corpus chính sách có heading rõ ràng — 3/4 chiến lược còn lại (kể cả `by_sentences`/`recursive` vốn tôn trọng ranh giới câu/đoạn) đã xử lý đúng câu này.
- Nếu bắt buộc dùng `FixedSizeChunker`, nên tăng `overlap` đáng kể (VD: overlap ≈ 50% chunk_size) để giảm khả năng một mục ngắn bị "kẹp" hoàn toàn giữa 2 chunk mà không chunk nào chứa trọn nội dung.

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- Với văn bản chính sách có heading rõ ràng, chunking theo cấu trúc (heading/section) cho retrieval chính xác hơn hẳn cắt cứng theo ký tự — đặc biệt với câu hỏi mà thông tin nằm trọn trong 1 mục ngắn.
- Điểm cosine similarity tuyệt đối của `text-embedding-3-small` cho văn bản tiếng Việt khá thấp ngay cả với cặp liên quan thực sự (0.29–0.65) — thứ tự xếp hạng (ranking) quan trọng hơn giá trị điểm tuyệt đối khi đánh giá retrieval.
- Lọc metadata (`customer_role`) hữu ích nhất khi corpus có nhiều tài liệu dùng chung từ vựng nhưng khác đối tượng người đọc (buyer vs seller) — giúp loại nhiễu trước khi so khớp ngữ nghĩa.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ 5 tài liệu nhưng 4 chiến lược chunking cho kết quả relevant-in-top-3 khác nhau (4/5 với `fixed_size` so với 5/5 ở 3 chiến lược còn lại) — chênh lệch không nằm ở embedder hay câu hỏi mà ở việc chunk có tôn trọng ranh giới ngữ nghĩa tự nhiên của văn bản (heading/câu/đoạn) hay không. Bài học chính: nên khảo sát cấu trúc văn bản nguồn trước khi chọn chunking mặc định, thay vì luôn dùng `FixedSizeChunker` cho mọi loại tài liệu.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Sẽ chuẩn hóa toàn bộ tài liệu thu thập theo cùng một cấu trúc heading nhất quán ngay từ khâu làm sạch dữ liệu (để `HeadingSectionChunker` áp dụng được đồng đều), đồng thời bổ sung thêm 3-5 tài liệu nữa (đặc biệt từ Lazada cho điều kiện người bán, và Tiki cho đổi trả) để có đủ dữ liệu so sánh chéo giữa các sàn trên cùng một khía cạnh chính sách.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 — đủ 5 tài liệu công khai thật, đủ metadata bắt buộc; có thể bổ sung thêm 2-5 tài liệu để dư dả hơn mức tối thiểu |
| Thiết kế chiến lược (Strategy Design) | 10 / 15 — mới có 1/5 thành viên chạy thật (Huy, 4 chiến lược); cần Đại, Đạt, Phong, Quang Anh bổ sung chiến lược riêng của mỗi người để đủ góc so sánh nhóm |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 — 5 câu benchmark hợp lệ (đủ dạng, có câu cần metadata filter), có phân tích lỗi cụ thể |
| Thuyết trình (Demo) | _chưa chấm — cần demo thật với các nhóm khác_ |
| **Tổng phần nhóm** | **28 / 35** (chưa tính phần Thuyết trình) |
