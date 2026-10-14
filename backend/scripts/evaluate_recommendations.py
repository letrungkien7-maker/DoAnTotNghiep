"""
BENCHMARK & EVALUATION SCRIPT: REAL ESTATE RECOMMENDATION ENGINE
Compares Traditional Boolean Hard-Filter Search vs Multi-Criteria Recommendation Scoring.
Calculates Precision@K, Recall@K, and NDCG@K on an annotated benchmark dataset.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from app.schemas.recommendation import RecommendationCriteria
from app.services.recommendation_engine import RecommendationEngine


@dataclass
class BenchmarkListing:
    id: int
    title: str
    category_id: int
    category_name: str
    transaction_type: str
    price: float
    area: float
    bedrooms: int
    province: str
    district: str
    features: List[str] = field(default_factory=list)


# 1. Benchmark Candidate Catalog (20 Diverse Listings)
CATALOG: List[BenchmarkListing] = [
    # Căn hộ Nam Từ Liêm / Cầu Giấy (Hà Nội)
    BenchmarkListing(1, "Căn hộ 2PN Vinhomes Smart City Tây Mỗ", 1, "Căn hộ chung cư", "SALE", 3_200_000_000, 65.0, 2, "Hà Nội", "Nam Từ Liêm", ["Nội thất đầy đủ", "Sổ đỏ chính chủ", "Bể bơi"]),
    BenchmarkListing(2, "Căn hộ 2PN Masteri West Heights view hồ", 1, "Căn hộ chung cư", "SALE", 3_450_000_000, 68.0, 2, "Hà Nội", "Nam Từ Liêm", ["Nội thất đầy đủ", "Bể bơi"]),
    BenchmarkListing(3, "Căn hộ 2PN Imperia Smart City giá tốt", 1, "Căn hộ chung cư", "SALE", 3_250_000_000, 64.0, 2, "Hà Nội", "Nam Từ Liêm", ["Sổ đỏ chính chủ"]),
    BenchmarkListing(4, "Căn hộ 3PN The Matrix One Mễ Trì", 1, "Căn hộ chung cư", "SALE", 5_800_000_000, 112.0, 3, "Hà Nội", "Nam Từ Liêm", ["Nội thất cao cấp", "Gara ô tô"]),
    BenchmarkListing(5, "Căn hộ 2PN D'Capitale Trần Duy Hưng", 1, "Căn hộ chung cư", "SALE", 4_300_000_000, 72.0, 2, "Hà Nội", "Cầu Giấy", ["Nội thất đầy đủ", "Sổ đỏ chính chủ"]),
    BenchmarkListing(6, "Căn hộ 1PN Vinhomes Smart City Studio", 1, "Căn hộ chung cư", "SALE", 1_850_000_000, 36.0, 1, "Hà Nội", "Nam Từ Liêm", ["Nội thất cơ bản"]),

    # Nhà phố / Liền kề Hà Đông & Thanh Xuân (Hà Nội)
    BenchmarkListing(7, "Nhà liền kề Geleximco Lê Trọng Tấn 100m2", 2, "Nhà riêng - Nhà phố", "SALE", 8_500_000_000, 100.0, 4, "Hà Nội", "Hà Đông", ["Gara ô tô", "Sổ đỏ chính chủ", "Mặt tiền 5m"]),
    BenchmarkListing(8, "Nhà phân lô KĐT Văn Phú Hà Đông 90m2", 2, "Nhà riêng - Nhà phố", "SALE", 9_200_000_000, 90.0, 4, "Hà Nội", "Hà Đông", ["Gara ô tô", "Sổ đỏ chính chủ"]),
    BenchmarkListing(9, "Nhà mặt phố Quang Trung Hà Đông kinh doanh", 2, "Nhà riêng - Nhà phố", "SALE", 12_500_000_000, 85.0, 5, "Hà Nội", "Hà Đông", ["Mặt tiền lớn", "Kinh doanh"]),
    BenchmarkListing(10, "Nhà riêng ngõ ô tô Nguyễn Trãi Thanh Xuân", 2, "Nhà riêng - Nhà phố", "SALE", 7_900_000_000, 65.0, 4, "Hà Nội", "Thanh Xuân", ["Sổ đỏ chính chủ"]),

    # BĐS Cho thuê (Hà Nội)
    BenchmarkListing(11, "Cho thuê căn hộ 2PN FLC Cầu Giấy full đồ", 1, "Căn hộ chung cư", "RENT", 14_000_000, 70.0, 2, "Hà Nội", "Cầu Giấy", ["Nội thất đầy đủ", "Thang máy"]),
    BenchmarkListing(12, "Cho thuê căn hộ 2PN Discovery Complex", 1, "Căn hộ chung cư", "RENT", 16_500_000, 85.0, 2, "Hà Nội", "Cầu Giấy", ["Nội thất cao cấp", "Bể bơi"]),
    BenchmarkListing(13, "Cho thuê nhà nguyên căn ngõ Cầu Giấy", 2, "Nhà riêng - Nhà phố", "RENT", 22_000_000, 80.0, 4, "Hà Nội", "Cầu Giấy", ["Kinh doanh online"]),

    # Biệt thự nghỉ dưỡng & Đất nền (Đà Nẵng & TP.HCM)
    BenchmarkListing(14, "Biệt thự biển Sơn Trà Ocean View Đà Nẵng", 3, "Biệt thự nghỉ dưỡng", "SALE", 18_500_000_000, 320.0, 4, "Đà Nẵng", "Sơn Trà", ["Hồ bơi riêng", "Sổ đỏ chính chủ", "View biển"]),
    BenchmarkListing(15, "Biệt thự Furama Resort Đà Nẵng 3PN", 3, "Biệt thự nghỉ dưỡng", "SALE", 16_800_000_000, 280.0, 3, "Đà Nẵng", "Ngũ Hành Sơn", ["Hồ bơi riêng", "Nội thất cao cấp"]),
    BenchmarkListing(16, "Đất nền ven sông Hòa Xuân Đà Nẵng 100m2", 4, "Đất nền dự án", "SALE", 3_600_000_000, 100.0, 0, "Đà Nẵng", "Cẩm Lệ", ["Sổ đỏ chính chủ"]),
    BenchmarkListing(17, "Căn hộ 2PN Vinhomes Central Park Bình Thạnh", 1, "Căn hộ chung cư", "SALE", 5_600_000_000, 78.0, 2, "Hồ Chí Minh", "Bình Thạnh", ["View sông", "Nội thất đầy đủ"]),
    BenchmarkListing(18, "Căn hộ 3PN Masteri Thảo Điền Quận 2", 1, "Căn hộ chung cư", "SALE", 7_200_000_000, 95.0, 3, "Hồ Chí Minh", "Thủ Đức", ["Nội thất cao cấp", "Bể bơi"]),
    BenchmarkListing(19, "Nhà phố KĐT Sala Thủ Thiêm Quận 2", 2, "Nhà riêng - Nhà phố", "SALE", 35_000_000_000, 160.0, 4, "Hồ Chí Minh", "Thủ Đức", ["Hầm xe", "Thang máy"]),
    BenchmarkListing(20, "Căn hộ Studio Masteri An Phú", 1, "Căn hộ chung cư", "RENT", 12_000_000, 45.0, 1, "Hồ Chí Minh", "Thủ Đức", ["Nội thất đầy đủ"]),
]


# 2. Benchmark Queries & Ground-Truth Relevance Annotations
# Scale: 3 = Perfect Match, 2 = Highly Relevant, 1 = Partially Relevant, 0 = Irrelevant
# (Relevance threshold for Precision/Recall is relevance >= 2)
BENCHMARK_SCENARIOS = [
    {
        "id": "Q1",
        "description": "Vợ chồng trẻ tìm căn hộ 2PN tại Nam Từ Liêm, ngân sách 3.0 - 3.5 tỷ, ưu tiên có nội thất",
        "criteria": RecommendationCriteria(
            transaction_type="SALE",
            category_id=1,
            province="Hà Nội",
            district="Nam Từ Liêm",
            budget_min=3_000_000_000,
            budget_max=3_500_000_000,
            bedrooms=2,
            features=["Nội thất đầy đủ"],
            top_k=5,
        ),
        "ground_truth": {1: 3, 2: 3, 3: 2, 5: 1, 6: 1, 4: 0, 7: 0, 11: 0},
    },
    {
        "id": "Q2",
        "description": "Gia đình cần tìm nhà liền kề Hà Đông, 4 phòng ngủ, ngân sách 8.0 - 9.5 tỷ, có gara",
        "criteria": RecommendationCriteria(
            transaction_type="SALE",
            category_id=2,
            province="Hà Nội",
            district="Hà Đông",
            budget_min=8_000_000_000,
            budget_max=9_500_000_000,
            bedrooms=4,
            features=["Gara ô tô"],
            top_k=5,
        ),
        "ground_truth": {7: 3, 8: 3, 10: 2, 9: 1, 1: 0, 14: 0},
    },
    {
        "id": "Q3 (Near Boundary Case)",
        "description": "Khách ngân sách tối đa 3.2 tỷ tại Nam Từ Liêm (Căn hộ 3.25B bị lọc mất nếu dùng Hard Filter)",
        "criteria": RecommendationCriteria(
            transaction_type="SALE",
            category_id=1,
            province="Hà Nội",
            district="Nam Từ Liêm",
            budget_max=3_200_000_000,
            bedrooms=2,
            top_k=5,
        ),
        "ground_truth": {1: 3, 3: 3, 2: 2, 6: 1, 5: 0, 7: 0},
    },
    {
        "id": "Q4",
        "description": "Người đi làm thuê căn hộ Cầu Giấy 2PN dưới 15 triệu/tháng, full đồ",
        "criteria": RecommendationCriteria(
            transaction_type="RENT",
            category_id=1,
            province="Hà Nội",
            district="Cầu Giấy",
            budget_max=15_000_000,
            bedrooms=2,
            features=["Nội thất đầy đủ"],
            top_k=5,
        ),
        "ground_truth": {11: 3, 12: 2, 13: 1, 20: 0, 1: 0},
    },
    {
        "id": "Q5",
        "description": "Nhà đầu tư tìm biệt thự nghỉ dưỡng Đà Nẵng view biển, ngân sách 15 - 20 tỷ",
        "criteria": RecommendationCriteria(
            transaction_type="SALE",
            category_id=3,
            province="Đà Nẵng",
            budget_min=15_000_000_000,
            budget_max=20_000_000_000,
            features=["View biển"],
            top_k=5,
        ),
        "ground_truth": {14: 3, 15: 3, 16: 1, 1: 0, 7: 0},
    },
]


def run_hard_filter_search(catalog: List[BenchmarkListing], crit: RecommendationCriteria) -> List[BenchmarkListing]:
    """Simulates traditional exact-match Boolean SQL filtering."""
    results = []
    for l in catalog:
        if crit.transaction_type and l.transaction_type != crit.transaction_type:
            continue
        if crit.category_id and l.category_id != crit.category_id:
            continue
        if crit.province and l.province != crit.province:
            continue
        if crit.district and l.district != crit.district:
            continue
        if crit.budget_min and l.price < crit.budget_min:
            continue
        if crit.budget_max and l.price > crit.budget_max:
            continue
        if crit.bedrooms and l.bedrooms != crit.bedrooms:
            continue
        # Hard check features if present
        if crit.features:
            norm_l = {f.lower() for f in l.features}
            if not all(f.lower() in norm_l for f in crit.features):
                continue
        results.append(l)
    return results[: crit.top_k]


def run_recommendation_scoring(catalog: List[BenchmarkListing], crit: RecommendationCriteria) -> List[BenchmarkListing]:
    """Runs the proposed Multi-Criteria Recommendation Engine."""
    scored = []
    for l in catalog:
        # Hard constraint: transaction type must match
        if crit.transaction_type and l.transaction_type != crit.transaction_type:
            continue
        # Hard constraint: province if specified must match
        if crit.province and l.province != crit.province:
            continue

        breakdown, _ = RecommendationEngine.score_listing(l, crit)
        scored.append((breakdown.total_score, l))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [l for _, l in scored[: crit.top_k]]


# 3. Metric Calculations
def calculate_precision_at_k(recommended_ids: List[int], ground_truth: Dict[int, int], k: int) -> float:
    top_k = recommended_ids[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(1 for item_id in top_k if ground_truth.get(item_id, 0) >= 2)
    return relevant_count / len(top_k)


def calculate_recall_at_k(recommended_ids: List[int], ground_truth: Dict[int, int], k: int) -> float:
    top_k = recommended_ids[:k]
    total_relevant = sum(1 for item_id, rel in ground_truth.items() if rel >= 2)
    if total_relevant == 0:
        return 1.0
    retrieved_relevant = sum(1 for item_id in top_k if ground_truth.get(item_id, 0) >= 2)
    return retrieved_relevant / total_relevant


def calculate_ndcg_at_k(recommended_ids: List[int], ground_truth: Dict[int, int], k: int) -> float:
    top_k = recommended_ids[:k]
    if not top_k:
        return 0.0

    # DCG
    dcg = 0.0
    for idx, item_id in enumerate(top_k):
        rel = ground_truth.get(item_id, 0)
        dcg += (2**rel - 1) / math.log2(idx + 2)

    # Ideal DCG (IDCG)
    ideal_rels = sorted(ground_truth.values(), reverse=True)[:k]
    idcg = 0.0
    for idx, rel in enumerate(ideal_rels):
        idcg += (2**rel - 1) / math.log2(idx + 2)

    if idcg == 0.0:
        return 1.0
    return dcg / idcg


def main():
    print("=" * 75)
    print("  KẾT QUẢ ĐÁNH GIÁ THỰC NGHIỆM THUẬT TOÁN GỢI Ý BẤT ĐỘNG SẢN")
    print("  So sánh: Boolean Hard-Filter (Truyền thống) vs Multi-Criteria Recommender")
    print("=" * 75)

    ks = [3, 5]
    metrics_hard = {f"P@{k}": [] for k in ks}
    metrics_hard.update({f"R@{k}": [] for k in ks})
    metrics_hard.update({f"NDCG@{k}": [] for k in ks})
    zero_results_hard = 0

    metrics_rec = {f"P@{k}": [] for k in ks}
    metrics_rec.update({f"R@{k}": [] for k in ks})
    metrics_rec.update({f"NDCG@{k}": [] for k in ks})
    zero_results_rec = 0

    for scenario in BENCHMARK_SCENARIOS:
        crit = scenario["criteria"]
        gt = scenario["ground_truth"]

        # Run Baseline Hard Filter
        res_hard = run_hard_filter_search(CATALOG, crit)
        ids_hard = [l.id for l in res_hard]
        if len(ids_hard) == 0:
            zero_results_hard += 1

        # Run Recommendation Engine
        res_rec = run_recommendation_scoring(CATALOG, crit)
        ids_rec = [l.id for l in res_rec]
        if len(ids_rec) == 0:
            zero_results_rec += 1

        for k in ks:
            metrics_hard[f"P@{k}"].append(calculate_precision_at_k(ids_hard, gt, k))
            metrics_hard[f"R@{k}"].append(calculate_recall_at_k(ids_hard, gt, k))
            metrics_hard[f"NDCG@{k}"].append(calculate_ndcg_at_k(ids_hard, gt, k))

            metrics_rec[f"P@{k}"].append(calculate_precision_at_k(ids_rec, gt, k))
            metrics_rec[f"R@{k}"].append(calculate_recall_at_k(ids_rec, gt, k))
            metrics_rec[f"NDCG@{k}"].append(calculate_ndcg_at_k(ids_rec, gt, k))

    num_scenarios = len(BENCHMARK_SCENARIOS)

    print("\n--- BẢNG ĐO LƯỜNG ĐỘ CHÍNH XÁC & ĐỘ PHỦ TRUNG BÌNH ---")
    header = f"{'Chỉ số đo lường':<18} | {'Hard-Filter Search':<20} | {'Recommendation Engine':<22} | {'Độ cải thiện':<15}"
    print(header)
    print("-" * len(header))

    all_keys = [f"P@{k}" for k in ks] + [f"R@{k}" for k in ks] + [f"NDCG@{k}" for k in ks]
    for key in all_keys:
        avg_h = sum(metrics_hard[key]) / num_scenarios
        avg_r = sum(metrics_rec[key]) / num_scenarios
        diff = avg_r - avg_h
        pct = (diff / avg_h * 100) if avg_h > 0 else 100.0
        sign = "+" if diff >= 0 else ""
        print(f"{key:<18} | {avg_h:<20.4f} | {avg_r:<22.4f} | {sign}{diff:.4f} ({sign}{pct:.1f}%)")

    print("-" * len(header))
    zero_h_rate = (zero_results_hard / num_scenarios) * 100
    zero_r_rate = (zero_results_rec / num_scenarios) * 100
    print(f"{'Tỷ lệ kết quả rỗng':<18} | {zero_h_rate:<19.1f}% | {zero_r_rate:<21.1f}% | -{zero_h_rate - zero_r_rate:.1f}%")
    print("=" * 75)


if __name__ == "__main__":
    main()
