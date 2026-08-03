"""
bench.py — Chạy bộ 5 câu hỏi đánh giá (benchmark) của nhóm trên nhiều chiến lược chunking.

Dùng cho demo (mục 8 — Report, demo và nộp bài): mở sẵn terminal, chạy lệnh này để
xem bảng so sánh top-1/top-3 của từng chiến lược trên 5 benchmark query, hoặc chạy
một câu hỏi tự do (live query) để minh họa trực tiếp.

Cách chạy:
    python bench.py                         # chạy đủ 5 benchmark query trên mọi chiến lược
    python bench.py --strategy heading_custom   # chỉ chạy 1 chiến lược, in chi tiết top-3
    python bench.py --query "câu hỏi tự do của bạn"   # live query trên mọi chiến lược

Mặc định dùng EMBEDDING_PROVIDER trong .env (xem README.md mục Tùy Chọn Mô Hình Nhúng).
Nếu không đặt gì, rơi về mock embedder — kết quả chỉ mang tính minh họa cấu trúc,
KHÔNG phản ánh chất lượng ngữ nghĩa thật (xem README.md).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

from ingest import chunk_document, load_documents
from main import _select_embedder
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.store import EmbeddingStore

DEFAULT_DATA_DIR = "data/k4_ecommerce"


class HeadingSectionChunker:
    """Chia nhỏ theo tiêu đề mục (## ...) - phù hợp văn bản chính sách có cấu trúc heading rõ ràng.

    Lý do thiết kế: các file chính sách TMĐT trong data/k4_ecommerce/ đều được tổ chức
    theo mục (## Điều kiện..., ## Thời hạn...) - mỗi mục là một đơn vị ngữ nghĩa trọn vẹn,
    tách theo heading giữ nguyên ngữ cảnh của từng điều khoản thay vì cắt cứng theo ký tự.
    """

    def __init__(self, max_chunk_size: int = 800) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            if len(section) <= self.max_chunk_size:
                chunks.append(section)
            else:
                chunks.extend(RecursiveChunker(chunk_size=self.max_chunk_size).chunk(section))
        return chunks


STRATEGIES = {
    "fixed_size": lambda: FixedSizeChunker(chunk_size=300, overlap=30),
    "by_sentences": lambda: SentenceChunker(max_sentences_per_chunk=3),
    "recursive": lambda: RecursiveChunker(chunk_size=300),
    "heading_custom": lambda: HeadingSectionChunker(max_chunk_size=800),
}

# Bộ 5 câu hỏi đánh giá của nhóm — phải khớp với REPORT_NHOM.md Phần 3.
BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Nếu người bán giao sai kích cỡ hoặc màu sản phẩm thì tôi có được yêu cầu trả hàng không?",
        "gold": "Có — người bán giao sai sản phẩm (sai kích cỡ, màu sắc) là điều kiện hợp lệ để yêu cầu trả hàng/hoàn tiền.",
        "expected_doc": "k4-returns-policy",
        "metadata_filter": None,
    },
    {
        "id": 2,
        "query": "Dịch vụ giao hàng hỏa tốc 4 giờ của Lazada áp dụng cho khu vực nào và giới hạn khối lượng sản phẩm là bao nhiêu?",
        "gold": "Nội thành Hà Nội và TP.HCM (không gồm ngoại thành); sản phẩm dưới 15kg, dưới 70cm, không áp dụng bỉm/tã.",
        "expected_doc": "k4-shipping-policy",
        "metadata_filter": None,
    },
    {
        "id": 3,
        "query": "Nhà bán có được đăng bán hàng cũ, đã qua sử dụng trên sàn không?",
        "gold": "Không — Tiki không hỗ trợ đăng bán hàng cũ, đã qua sử dụng, like new, hàng second hand.",
        "expected_doc": "k4-seller-listing",
        "metadata_filter": {"customer_role": "seller"},
    },
    {
        "id": 4,
        "query": "Nếu dùng Apple Pay để thanh toán thì giá trị đơn hàng tối đa được hỗ trợ là bao nhiêu?",
        "gold": "25.000.000 VNĐ (phạm vi từ 10.000đ đến 25.000.000đ).",
        "expected_doc": "k4-payment-methods",
        "metadata_filter": None,
    },
    {
        "id": 5,
        "query": "Sàn có chia sẻ dữ liệu cá nhân của tôi với cơ quan chính phủ không?",
        "gold": "Có, khi được yêu cầu theo pháp luật.",
        "expected_doc": "k4-privacy-policy",
        "metadata_filter": None,
    },
]


def build_stores(data_dir: str, embedder, strategy_names: list[str]) -> dict[str, EmbeddingStore]:
    docs = load_documents(data_dir)
    stores: dict[str, EmbeddingStore] = {}
    for name in strategy_names:
        chunker = STRATEGIES[name]()
        chunk_docs = []
        for doc in docs:
            chunk_docs.extend(chunk_document(doc, chunker))
        store = EmbeddingStore(collection_name=f"bench_{name}", embedding_fn=embedder)
        store.add_documents(chunk_docs)
        stores[name] = store
    return stores, docs


def run_benchmark(stores: dict[str, EmbeddingStore], verbose: bool = False) -> None:
    tally = {name: 0 for name in stores}
    for q in BENCHMARK_QUERIES:
        print(f"\n--- Q{q['id']}: {q['query']}")
        print(f"    Gold: {q['gold']}")
        for name, store in stores.items():
            if q["metadata_filter"]:
                results = store.search_with_filter(q["query"], top_k=3, metadata_filter=q["metadata_filter"])
            else:
                results = store.search(q["query"], top_k=3)
            top_docs = [r["metadata"].get("doc_id") for r in results]
            relevant = q["expected_doc"] in top_docs
            tally[name] += int(relevant)
            top1 = results[0] if results else None
            score_str = f"{top1['score']:.4f}" if top1 else "N/A"
            flag = "OK" if relevant else "FAIL"
            print(f"    [{name:14s}] top1={top1['metadata'].get('doc_id') if top1 else None:20s} "
                  f"score={score_str} relevant-in-top3={flag}")
            if verbose and top1:
                print(f"        > {top1['content'][:150].replace(chr(10), ' ')}...")

    print("\n=== TỔNG KẾT (relevant-in-top-3 / 5 câu) ===")
    for name, count in tally.items():
        print(f"  {name:14s}: {count}/5")


def run_live_query(stores: dict[str, EmbeddingStore], query: str) -> None:
    print(f"\n=== LIVE QUERY: {query} ===")
    for name, store in stores.items():
        results = store.search(query, top_k=3)
        print(f"\n[{name}] top-3:")
        for i, r in enumerate(results, start=1):
            print(f"  {i}. score={r['score']:.4f} doc_id={r['metadata'].get('doc_id')}")
            print(f"     {r['content'][:150].replace(chr(10), ' ')}...")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=os.getenv("LAB_DATA_DIR", DEFAULT_DATA_DIR))
    parser.add_argument("--strategy", choices=list(STRATEGIES), default=None,
                        help="Chỉ chạy 1 chiến lược (mặc định: chạy cả 4 để so sánh)")
    parser.add_argument("--query", default=None, help="Chạy 1 câu hỏi tự do (live demo) thay vì bộ benchmark")
    args = parser.parse_args()

    load_dotenv(override=False)

    if not Path(args.data_dir).exists():
        print(f"Không tìm thấy thư mục dữ liệu: {args.data_dir}")
        return 1

    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print(f"Backend nhúng: {backend}")
    if backend == "mock embeddings fallback":
        print("Lưu ý: mock KHÔNG phản ánh chất lượng ngữ nghĩa thật — chỉ minh họa cấu trúc chạy.")

    strategy_names = [args.strategy] if args.strategy else list(STRATEGIES)
    stores, docs = build_stores(args.data_dir, embedder, strategy_names)
    print(f"Đã nạp {len(docs)} tài liệu, {sum(s.get_collection_size() for s in stores.values())} chunk (tổng mọi chiến lược)")

    if args.query:
        run_live_query(stores, args.query)
    else:
        run_benchmark(stores, verbose=bool(args.strategy))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
