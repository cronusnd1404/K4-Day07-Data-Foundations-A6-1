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

> Huy đã chạy cả 4 chiến lược (3 built-in + 1 custom) trên cùng bộ 5 tài liệu và 5 benchmark query bằng `bench.py` (chi tiết ở Phần 3) để có đường so sánh đầy đủ trong lúc chờ các thành viên khác bổ sung. Đánh giá "liên quan" dùng 2 mức: **doc-level** (top-3 có đúng tài liệu nguồn không) và **content-level** (chunk top-3 có thực sự chứa câu trả lời, kiểm bằng từ khóa gold-answer, không chỉ đúng tài liệu).

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Huy | FixedSizeChunker (baseline) | 8/10 (5/5 đúng doc, 4/5 đúng content) | Đơn giản, chunk đều nhau, dễ dự đoán chi phí embedding | Cắt cứng theo ký tự nên hay đứt ngay đầu mục chính sách — ở Q2 (giao hàng hỏa tốc), top-3 đều thuộc đúng doc nhưng không chunk nào chứa cụm "hỏa tốc" vì chunk bị cắt ngay sau đoạn tiêu đề mục |
| Huy | SentenceChunker | 10/10 (5/5 đúng doc, 5/5 đúng content) | Theo ranh giới câu nên không cắt ngang ý; nội dung mục nào cũng lọt trọn vào ít nhất 1 chunk | Một mục chính sách nhiều câu bị tách thành nhiều chunk nhỏ rời rạc, có thể mất liên kết giữa các câu trong cùng điều khoản |
| Huy | RecursiveChunker | 8/10 (5/5 đúng doc, 4/5 đúng content) | Cân bằng giữa giữ ngữ cảnh và kích thước chunk ổn định | Tách theo đoạn (`\n\n`) đôi khi tạo ra chunk gần như rỗng (chỉ có tiêu đề `#`/`##`) — chunk này lại có điểm similarity cao do khớp từ khóa chung, đẩy chunk chứa nội dung thật ra khỏi top-3 (xem Q5, Phần 4) |
| Huy | HeadingSectionChunker (custom) | 10/10 (5/5 đúng doc, 5/5 đúng content) | Giữ trọn từng điều khoản/mục chính sách theo đúng cấu trúc văn bản gốc; điểm similarity top-1 cao nhất ở 2/5 câu (Q1, Q2) | Phụ thuộc format có heading `##` rõ ràng; không tổng quát cho văn bản không có cấu trúc heading |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Xét theo **content-level** (chunk có thực sự chứa câu trả lời hay không — thước đo sát với chất lượng RAG thật hơn là chỉ đúng tài liệu), **`SentenceChunker`** và **`HeadingSectionChunker` (custom)** đều đạt 5/5, trong khi `FixedSizeChunker` và `RecursiveChunker` mỗi chiến lược hụt đúng 1 câu — nhưng ở **hai câu khác nhau** (Q2 và Q5), chứng tỏ lỗi không nằm ở embedder/câu hỏi mà ở cách mỗi chiến lược đặt ranh giới chunk. Giữa hai chiến lược thắng, `HeadingSectionChunker` được khuyến nghị làm mặc định cho corpus này vì mỗi chunk trùng khớp with một điều khoản chính sách trọn vẹn (dễ trích dẫn, dễ đọc khi demo) và có điểm similarity top-1 cao nhất ở 2/5 câu hỏi (Q1: 0.7013, Q2: 0.7179) — trong khi `SentenceChunker` tuy cũng đạt 5/5 content-level nhưng chunk nhỏ vụn hơn, khó trích dẫn nguyên một điều khoản khi trả lời.

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
> Chạy bằng `bench.py` với embedder OpenAI `text-embedding-3-small`, 4 chiến lược (fixed_size / by_sentences / recursive / heading_custom), `top_k=3`. "Đúng doc" = top-3 chứa tài liệu nguồn đúng; "đúng content" = ít nhất 1 chunk trong top-3 thực sự chứa cụm từ trả lời (kiểm chặt hơn). Chi tiết điểm số ở Phần 2.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Đúng doc / Đúng content (top-3)? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Giao sai kích cỡ/màu | `heading_custom` (score top-1 0.7013) | Đúng doc + đúng content ở cả 4 chiến lược | Mọi chiến lược đều truy xuất đúng và có nội dung trả lời |
| 2 | Giao hàng hỏa tốc Lazada | `heading_custom` (score top-1 0.7179) | Đúng doc ở cả 4; **đúng content chỉ 3/4** — `fixed_size` sai ở mức content | `fixed_size`: top-3 đều thuộc đúng doc nhưng chunk bị cắt ngay sau tiêu đề mục, mất cụm "hỏa tốc" — xem Phần 4 |
| 3 | Hàng cũ trên Tiki (lọc `seller`) | `recursive` (score top-1 0.5056, cao nhất) | Đúng doc + đúng content ở cả 4 chiến lược | Dùng `search_with_filter(metadata_filter={"customer_role":"seller"})` — loại bỏ ngay các chunk buyer-facing không liên quan trước khi so khớp |
| 4 | Giới hạn Apple Pay | `fixed_size` (score top-1 0.7142, cao nhất) | Đúng doc + đúng content ở cả 4 chiến lược | Câu hỏi có số liệu/tên riêng cụ thể ("Apple Pay") nên mọi chiến lược đều nhận diện tốt |
| 5 | Chia sẻ dữ liệu chính phủ | `fixed_size` (score top-1 0.5732) | Đúng doc ở cả 4; **đúng content chỉ 3/4** — `recursive` sai ở mức content | `recursive`: top-1 là chunk gần như rỗng (chỉ có tiêu đề `#`/`##`) — xem phân tích lỗi chi tiết ở Phần 4 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có — rõ nhất ở **Câu 3**. Khi lọc `metadata_filter={"customer_role": "seller"}` trước khi search, toàn bộ chunk buyer-facing (đổi trả, thanh toán, vận chuyển) bị loại khỏi tập ứng viên ngay từ đầu, nên kết quả top-3 chỉ còn cạnh tranh giữa các chunk của `k4-seller-listing` — giảm nguy cơ một chunk buyer vô tình có điểm similarity cao hơn do trùng từ khóa chung ("sản phẩm", "hàng hóa"). Với 4 câu còn lại, nội dung đã đủ đặc trưng theo doc nên filter không thay đổi nhiều, nhưng với corpus lớn hơn (nhiều tài liệu hơn/nhiều role hơn) lợi ích của filter sẽ rõ hơn.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

### Phân tích lỗi (Bài tập 3.5 — Failure Analysis)

**Câu hỏi thất bại:** Câu 5 — "Sàn có chia sẻ dữ liệu cá nhân của tôi với cơ quan chính phủ không?" — với chiến lược `RecursiveChunker` (chunk_size=300).

**Chi tiết (bằng chứng từ top-3 thật, chạy bằng `bench.py`):**

```
1. score=0.5222  k4-privacy-policy
   "# Chính sách bảo mật Shopee

   ## Loại dữ liệu cá nhân được thu thập"

2. score=0.5125  k4-privacy-policy
   "- Rút lại sự đồng ý cho việc xử lý dữ liệu. - Yêu cầu Shopee cung cấp dữ liệu
   cá nhân của chính người dùng. ... Liên hệ: dpo.vn@shopee.com..."

3. score=0.4779  k4-privacy-policy
   "- Thông tin cá nhân: họ tên, địa chỉ email... - Thông tin tài chính:..."
```

Top-3 đều đúng **tài liệu** (`k4-privacy-policy`) nhưng **không chunk nào chứa** mục "Chia sẻ dữ liệu với bên thứ ba" — đoạn thực sự trả lời câu hỏi ("Cơ quan chính phủ khi được yêu cầu theo pháp luật"). Nếu chỉ chấm theo tiêu chí "đúng tài liệu trong top-3" thì câu này trông như "đạt", nhưng agent nhận context này **không thể trả lời đúng** vì thông tin cốt lõi vắng mặt hoàn toàn — đây là lý do REPORT_NHOM.md dùng thêm tiêu chí "đúng content" song song với "đúng doc" (xem Phần 3).

**Tại sao thất bại:**
- `RecursiveChunker` tách theo `\n\n` (đoạn) trước tiên. Ngay đầu file, dòng tiêu đề `# Chính sách bảo mật Shopee` và heading `## Loại dữ liệu cá nhân được thu thập` đứng thành một "đoạn" gần như trống nội dung (chỉ có 2 dòng tiêu đề, chưa có thân bài) — nó bị tách thành 1 chunk riêng do đứng trước một `\n\n` khác.
- Chunk gần-như-rỗng này lại vô tình có **điểm similarity cao nhất** (0.5222) vì câu hỏi chứa các từ khóa chung ("chính sách bảo mật", "dữ liệu cá nhân") trùng với chính tiêu đề — embedding khớp bề mặt tiêu đề chứ không khớp nội dung cụ thể ("chia sẻ... cơ quan chính phủ").
- Chunk thật sự chứa câu trả lời (mục "Chia sẻ dữ liệu với bên thứ ba") bị chunk tiêu đề và 2 chunk khác (`Quyền của người dùng`, `Loại dữ liệu...`) lấn hết 3 vị trí top-3, nên bị đẩy ra ngoài — dù nó tồn tại trong store.
- Đây là lỗi **do ranh giới chunk** (một mẩu tiêu đề trở thành "chunk mồi nhử" điểm cao), không phải do thiếu metadata hay câu hỏi mơ hồ.

**Đề xuất cải thiện:**
- Gộp tiêu đề/heading rỗng vào chunk nội dung theo sau thay vì để đứng riêng — ví dụ `HeadingSectionChunker` (custom) tách theo `## ` nên mỗi chunk có heading kèm nội dung đầy đủ ngay sau, tránh được tình huống này (kiểm tra thực tế: `heading_custom` trả đúng chunk "Chia sẻ dữ liệu với bên thứ ba" ở hạng 2/3).
- `SentenceChunker` cũng tránh được lỗi này vì nó không coi tiêu đề đứng một mình là một đơn vị tách riêng.
- Nếu vẫn dùng `RecursiveChunker`, nên lọc bỏ hoặc gộp các "đoạn" ngắn hơn một ngưỡng ký tự (VD: <50 ký tự) vào đoạn liền sau trước khi tách tiếp, để tránh tạo chunk tiêu-đề-đơn-độc.

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- "Đúng tài liệu trong top-3" là điều kiện cần nhưng chưa đủ — phải kiểm cả nội dung chunk có thực sự chứa câu trả lời hay không; corpus này cho thấy 2 trong 4 chiến lược (`fixed_size` ở Q2, `recursive` ở Q5) đạt đúng-doc nhưng vẫn thất bại ở mức nội dung.
- Một chunk tiêu-đề-đơn-độc (gần như rỗng) có thể có điểm similarity **cao hơn** chunk chứa nội dung thật, vì embedding khớp từ khóa bề mặt của tiêu đề — cho thấy điểm số tuyệt đối không đủ tin cậy nếu không kiểm tra nội dung chunk.
- Lọc metadata (`customer_role`) hữu ích nhất khi corpus có nhiều tài liệu dùng chung từ vựng nhưng khác đối tượng người đọc (buyer vs seller) — giúp loại nhiễu trước khi so khớp ngữ nghĩa.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ 5 tài liệu nhưng 4 chiến lược chunking cho kết quả khác nhau ở mức nội dung (content-level: `by_sentences` và `heading_custom` đạt 5/5, `fixed_size` và `recursive` mỗi chiến lược hụt đúng 1 câu — nhưng là 2 câu khác nhau). Bài học chính: nên kiểm tra chunk có "đơn vị ngữ nghĩa trọn vẹn" hay không (không để tiêu đề đứng một mình, không cắt cứng xuyên ranh giới mục) trước khi chọn chunking mặc định, và luôn kiểm tra **nội dung** chunk retrieved chứ không chỉ tên tài liệu.

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
