"""
Dữ liệu bất động sản mẫu bao phủ toàn bộ 63 tỉnh/thành phố Việt Nam.
Tự động tích hợp vào hệ thống nạp dữ liệu (seed_demo_data.py).
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from app.models.listing import ListingStatus, TransactionType

# Danh sách Unsplash hình ảnh BĐS chất lượng cao
UNSPLASH_APARTMENTS = [
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
]

UNSPLASH_HOUSES = [
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
]

UNSPLASH_VILLAS = [
    "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=800&q=80",
]

UNSPLASH_LAND = [
    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80",
]

UNSPLASH_COMMERCIAL = [
    "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=800&q=80",
]

# Định nghĩa dữ liệu 63 tỉnh/thành phố
RAW_PROVINCES = [
    # (province, district, ward, title, category_id, trans_type, price, area, beds, baths, direction, legal, lat, lng, features)
    ("An Giang", "TP. Long Xuyên", "Mỹ Bình", "Nhà phố thương mại 3 tầng mặt tiền đường Trần Hưng Đạo", 2, "SALE", 4200000000, 110.0, 4, 3, "Đông Nam", "Sổ hồng riêng", 10.3759, 105.4358, ["Sổ đỏ chính chủ", "Gara ô tô", "Mặt tiền kinh doanh"]),
    ("Bà Rịa - Vũng Tàu", "TP. Vũng Tàu", "Thắng Tam", "Căn hộ condotel view biển Bãi Sau The Sóng Vũng Tàu", 1, "SALE", 2350000000, 52.0, 1, 1, "Đông", "Sổ hồng lâu dài", 10.3538, 107.0917, ["Nội thất đầy đủ", "Bể bơi", "View biển", "Thang máy"]),
    ("Bắc Giang", "TP. Bắc Giang", "Dĩnh Kế", "Đất nền phân lô KĐT Bách Việt Lake Garden sổ đỏ trao tay", 4, "SALE", 2100000000, 95.0, None, None, "Nam", "Sổ đỏ chính chủ", 21.2731, 106.2036, ["Sổ đỏ chính chủ", "Gần công viên", "Đường ô tô tránh"]),
    ("Bắc Kạn", "TP. Bắc Kạn", "Đức Xuân", "Nhà riêng 3 tầng kiên cố gần chợ trung tâm TP Bắc Kạn", 2, "SALE", 1650000000, 85.0, 3, 2, "Đông Bắc", "Sổ đỏ chính chủ", 22.1472, 105.8348, ["Sổ đỏ chính chủ", "Nội thất cơ bản"]),
    ("Bạc Liêu", "TP. Bạc Liêu", "Phường 7", "Nhà phố liền kề KĐT Hoàng Phát thiết kế hiện đại sang trọng", 2, "SALE", 2800000000, 100.0, 3, 3, "Tây Nam", "Sổ hồng riêng", 9.2941, 105.7278, ["Sổ đỏ chính chủ", "Gara ô tô", "Đường nhựa 12m"]),
    ("Bắc Ninh", "TP. Bắc Ninh", "Võ Cường", "Căn hộ cao cấp Vinhomes Bắc Ninh 2PN full nội thất cao cấp", 1, "RENT", 15000000, 72.0, 2, 2, "Đông Nam", "Hợp đồng thuê dài hạn", 21.1861, 106.0763, ["Nội thất đầy đủ", "Thang máy", "Bể bơi", "Phòng gym"]),
    ("Bến Tre", "TP. Bến Tre", "Phú Khương", "Biệt thự vườn sinh thái ven sông cây ăn trái trĩu quả", 3, "SALE", 5800000000, 450.0, 3, 3, "Nam", "Sổ hồng riêng", 10.2433, 106.3756, ["Sổ đỏ chính chủ", "Sân vườn rộng", "Bến thuyền riêng"]),
    ("Bình Định", "TP. Quy Nhơn", "Ghềnh Ráng", "Căn hộ cao cấp TMS Hotel Quy Nhơn view biển trực diện", 1, "SALE", 2600000000, 58.0, 2, 1, "Đông", "Sổ hồng sở hữu lâu dài", 13.7594, 109.2195, ["View biển", "Hồ bơi vô cực", "Nội thất đầy đủ"]),
    ("Bình Dương", "TP. Thủ Dầu Một", "Hiệp Thành", "Nhà phố thương mại 4 tầng mặt tiền Đại lộ Bình Dương", 2, "SALE", 6500000000, 120.0, 4, 4, "Tây", "Sổ hồng hoàn công", 10.9805, 106.6519, ["Sổ đỏ chính chủ", "Thang máy", "Kinh doanh tốt"]),
    ("Bình Phước", "TP. Đồng Xoài", "Tân Phú", "Đất nền thổ cư 100% gần KCN Đồng Xoài 3 pháp lý minh bạch", 4, "SALE", 950000000, 150.0, None, None, "Đông Nam", "Sổ đỏ trao tay", 11.5333, 106.8833, ["Sổ đỏ chính chủ", "Đường nhựa 16m", "Hạ tầng hoàn thiện"]),
    ("Bình Thuận", "TP. Phan Thiết", "Tiến Thành", "Biệt thự nghỉ dưỡng biển NovaWorld Phan Thiết bàn giao full đồ", 3, "SALE", 8900000000, 200.0, 3, 3, "Nam", "Hợp đồng mua bán CĐT", 10.8722, 108.0642, ["View biển", "Sân Golf", "Hồ bơi riêng", "Nội thất cao cấp"]),
    ("Cà Mau", "TP. Cà Mau", "Phường 5", "Nhà phố 1 trệt 2 lầu đường Ngô Quyền thuận tiện buôn bán", 2, "SALE", 3400000000, 90.0, 3, 3, "Đông Bắc", "Sổ hồng riêng", 9.1769, 105.1524, ["Sổ đỏ chính chủ", "Mặt tiền kinh doanh"]),
    ("Cần Thơ", "Quận Ninh Kiều", "An Khánh", "Căn hộ cao cấp Chung cư Cadif Hưng Phú 2PN view sông Hậu", 1, "SALE", 2150000000, 68.0, 2, 2, "Đông Nam", "Sổ hồng lâu dài", 10.0284, 105.7694, ["Nội thất đầy đủ", "View sông", "Thang máy thẻ từ"]),
    ("Cao Bằng", "TP. Cao Bằng", "Hợp Giang", "Nhà phố 3 tầng trung tâm phố đi bộ Kim Đồng TP Cao Bằng", 2, "SALE", 2950000000, 75.0, 3, 2, "Tây Bắc", "Sổ đỏ chính chủ", 22.6664, 105.9733, ["Sổ đỏ chính chủ", "Phố đi bộ sầm uất"]),
    ("Đà Nẵng", "Quận Sơn Trà", "Phước Mỹ", "Căn hộ cao cấp The Sang Residence 2PN view bãi biển Mỹ Khê", 1, "SALE", 3800000000, 82.5, 2, 2, "Đông", "Sổ hồng lâu dài", 16.0617, 108.2435, ["View biển", "Bể bơi tầng thượng", "Nội thất cao cấp"]),
    ("Đắk Lắk", "TP. Buôn Ma Thuột", "Tân Lợi", "Biệt thự phong cách Tây Nguyên KĐT EcoCity Premia Km7", 3, "SALE", 7500000000, 250.0, 4, 4, "Nam", "Sổ đỏ chính chủ", 12.7100, 108.0700, ["Sân vườn rộng", "Bể bơi", "An ninh 24/7"]),
    ("Đắk Nông", "TP. Gia Nghĩa", "Nghĩa Đức", "Đất nền view hồ sinh thái Thiên Nga không khí mát lành", 4, "SALE", 1250000000, 300.0, None, None, "Đông", "Sổ hồng riêng", 11.9964, 107.6944, ["View hồ", "Thích hợp làm homestay", "Đường bê tông"]),
    ("Điện Biên", "TP. Điện Biên Phủ", "Mường Thanh", "Nhà mặt phố đường Võ Nguyên Giáp kinh doanh buôn bán tấp nập", 2, "SALE", 4500000000, 92.0, 4, 3, "Đông Nam", "Sổ đỏ chính chủ", 21.3855, 103.0188, ["Mặt tiền phố lớn", "Sổ đỏ chính chủ"]),
    ("Đồng Nai", "TP. Biên Hòa", "Long Hưng", "Nhà phố thương mại KĐT Aqua City sinh thái ven sông Đồng Nai", 2, "SALE", 5600000000, 120.0, 3, 4, "Tây Nam", "Hợp đồng mua bán", 10.9012, 106.8522, ["Công viên bờ sông", "Bến du thuyền", "An ninh 24/7"]),
    ("Đồng Tháp", "TP. Sa Đéc", "Tân Quy Đông", "Nhà vườn nghỉ dưỡng ngay làng hoa Sa Đéc ngập tràn sắc hoa", 3, "SALE", 3600000000, 320.0, 3, 2, "Đông", "Sổ hồng riêng", 10.3060, 105.7533, ["Sân vườn cây kiểng", "Đường ô tô", "Khu du lịch"]),
    ("Gia Lai", "TP. Pleiku", "Hoa Lư", "Nhà phố 2 tầng hiện đại đường Phạm Văn Đồng gần sân bay Pleiku", 2, "SALE", 3100000000, 115.0, 3, 2, "Đông Bắc", "Sổ đỏ chính chủ", 13.9833, 108.0000, ["Sổ đỏ chính chủ", "Gara ô tô rộng"]),
    ("Hà Giang", "TP. Hà Giang", "Nguyễn Trãi", "Nhà riêng 3 tầng view sông Miện trung tâm hành chính tỉnh", 2, "SALE", 2400000000, 88.0, 3, 2, "Nam", "Sổ đỏ chính chủ", 22.8233, 104.9839, ["View sông thoáng đãng", "Sổ đỏ chính chủ"]),
    ("Hà Nam", "TP. Phủ Lý", "Liêm Chính", "Liền kề shophouse KĐT River Silk City ven sông Châu Giang", 2, "SALE", 3250000000, 85.0, 4, 3, "Đông Nam", "Sổ hồng lâu dài", 20.5333, 105.9167, ["KĐT sinh thái", "Bể bơi", "Sân tennis"]),
    ("Hà Nội", "Quận Cầu Giấy", "Trung Hòa", "Căn hộ D'Capitale 3PN view hồ điều hòa Trần Duy Hưng", 1, "SALE", 6200000000, 95.0, 3, 2, "Đông Nam", "Sổ hồng lâu dài", 21.0069, 105.7958, ["Thang máy", "Bể bơi", "Full nội thất xịn", "Gara ô tô"]),
    ("Hà Tĩnh", "TP. Hà Tĩnh", "Hà Huy Tập", "Căn hộ chung cư Vinhomes New Center 2PN tiện ích Vincom", 1, "SALE", 1750000000, 62.0, 2, 1, "Nam", "Sổ hồng chính chủ", 18.3428, 105.9058, ["Bể bơi ngoài trời", "Sân bóng đá", "An ninh 24/7"]),
    ("Hải Dương", "TP. Hải Dương", "Hải Tân", "Nhà phố Ecorivers Hải Dương biệt lập sinh thái chuẩn xanh", 2, "SALE", 4800000000, 90.0, 4, 4, "Đông", "Sổ đỏ lâu dài", 20.9167, 106.3333, ["Công viên cây xanh", "Hồ điều hòa", "Khu dân trí cao"]),
    ("Hải Phòng", "Quận Lê Chân", "Vĩnh Niệm", "Biệt thự song lập Vinhomes Marina Cầu Rào phong cách Hy Lạp", 3, "SALE", 13500000000, 180.0, 4, 4, "Đông Nam", "Sổ đỏ lâu dài", 20.8333, 106.6833, ["Biệt thự ven sông", "Bể bơi", "Khu an ninh cao cấp"]),
    ("Hậu Giang", "TP. Vị Thanh", "Phường 4", "Đất nền KĐT Cát Tường Western Pearl tiện ích chuẩn Singapore", 4, "SALE", 1100000000, 100.0, None, None, "Tây", "Sổ hồng từng nền", 9.7844, 105.4703, ["Công viên kỳ quan", "Đường nhựa 14m"]),
    ("Hòa Bình", "TP. Hòa Bình", "Dân Chủ", "Biệt thự ven hồ Hòa Bình Ivory Villas & Resort cảnh quan núi đồi", 3, "SALE", 6800000000, 400.0, 3, 3, "Bắc", "Sổ đỏ chính chủ", 20.8167, 105.3333, ["View núi hồ", "Bể bơi vô cực", "Sân golf"]),
    ("Hưng Yên", "Huyện Văn Giang", "Nghĩa Trụ", "Căn hộ cao cấp Masteri Waterfront Ocean Park 2 view biển nhân tạo", 1, "SALE", 3100000000, 65.0, 2, 2, "Đông", "Sổ hồng lâu dài", 20.9500, 105.9667, ["Biển nhân tạo", "Hồ bơi bốn mùa", "TTTM Vincom Mega Mall"]),
    ("Khánh Hòa", "TP. Nha Trang", "Lộc Thọ", "Căn hộ mặt tiền biển Trần Phú view vịnh ngọc Nha Trang", 1, "SALE", 4100000000, 75.0, 2, 2, "Đông", "Sổ hồng vĩnh viễn", 12.2388, 109.1967, ["Mặt tiền biển", "Hồ bơi tràn", "Nội thất nhập khẩu"]),
    ("Kiên Giang", "TP. Phú Quốc", "Dương Đông", "Shophouse phố đêm Grand World Phú Quốc kinh doanh 24/7", 5, "RENT", 35000000, 120.0, 0, 3, "Nam", "Hợp đồng thuê 5 năm", 10.2899, 103.8569, ["Thành phố không ngủ", "Gần Casino Corona", "Lượng khách đông"]),
    ("Kon Tum", "TP. Kon Tum", "Quang Trung", "Nhà phố 2 tầng khang trang gần bờ kè sông Đắk Bla", 2, "SALE", 2250000000, 105.0, 3, 2, "Đông", "Sổ đỏ chính chủ", 14.3500, 108.0000, ["Gần sông mát mẻ", "Khu dân cư an ninh"]),
    ("Lai Châu", "TP. Lai Châu", "Tân Phong", "Nhà riêng 3 tầng mặt đường lớn trung tâm quảng trường Lai Châu", 2, "SALE", 2600000000, 100.0, 4, 3, "Tây Nam", "Sổ đỏ chính chủ", 22.3964, 103.4589, ["Sổ đỏ chính chủ", "Gần quảng trường"]),
    ("Lâm Đồng", "TP. Đà Lạt", "Phường 10", "Biệt thự nghỉ dưỡng view đồi thông săn mây đường Khởi Nghĩa Bắc Sơn", 3, "SALE", 16500000000, 280.0, 5, 5, "Đông Nam", "Sổ hồng hoàn công", 11.9404, 108.4583, ["View đồi thông", "Sân vườn nướng BBQ", "Nội thất gỗ sồi"]),
    ("Lạng Sơn", "TP. Lạng Sơn", "Chi Lăng", "Nhà phố thương mại Shophouse Vincom Lạng Sơn kinh doanh tốt", 2, "SALE", 5200000000, 80.0, 4, 3, "Đông", "Sổ hồng lâu dài", 21.8500, 106.7500, ["Khu buôn bán sầm uất", "Vincom Plaza"]),
    ("Lào Cai", "Thị xã Sa Pa", "Phường Sa Pa", "Khách sạn mini 8 phòng view trọn thung lũng Mường Hoa Sa Pa", 2, "SALE", 9800000000, 135.0, 8, 8, "Tây Nam", "Sổ đỏ lâu dài", 22.3364, 103.8438, ["View thung lũng", "Đang kinh doanh tốt", "Full nội thất homestay"]),
    ("Long An", "Huyện Bến Lức", "An Thạnh", "Nhà phố vườn ven sông Vàm Cỏ Đông KĐT Waterpoint Bến Lức", 2, "SALE", 3900000000, 110.0, 3, 3, "Nam", "Sổ hồng riêng", 10.6333, 106.4833, ["Công viên bờ sông", "Bến du thuyền", "Vịnh nước ngọt"]),
    ("Nam Định", "TP. Nam Định", "Lộc Vượng", "Biệt thự đơn lập KĐT Dệt May Nam Định vị trí đắc địa", 3, "SALE", 7200000000, 220.0, 4, 4, "Đông Nam", "Sổ đỏ chính chủ", 20.4333, 106.1833, ["Khu dân trí cao", "Sân vườn", "Gara ô tô"]),
    ("Nghệ An", "TP. Vinh", "Hưng Hòa", "Nhà phố Eco Central Park Vinh đại công viên xanh lớn nhất miền Trung", 2, "SALE", 5500000000, 108.0, 4, 4, "Đông", "Sổ hồng lâu dài", 18.6667, 105.6667, ["Hồ điều hòa", "Công viên ánh sáng", "Rừng sinh thái"]),
    ("Ninh Bình", "TP. Ninh Bình", "Ninh Khánh", "Biệt thự sinh thái gần danh thắng Tràng An non nước hữu tình", 3, "SALE", 8500000000, 300.0, 4, 4, "Nam", "Sổ đỏ chính chủ", 20.2500, 105.9833, ["Cảnh quan núi đá", "Hồ cá koi", "Không gian nghỉ dưỡng"]),
    ("Ninh Thuận", "TP. Phan Rang - Tháp Chàm", "Mỹ Hải", "Căn hộ khách sạn SunBay Park Hotel & Resort view biển Bình Sơn", 1, "SALE", 1850000000, 48.0, 1, 1, "Đông", "Hợp đồng kinh doanh", 11.5667, 108.9833, ["View biển Bình Sơn", "Công viên nước", "Casino"]),
    ("Phú Thọ", "TP. Việt Trì", "Tiên Cát", "Nhà liền kề KĐT Đồng Mạ trung tâm Đất Tổ Việt Trì", 2, "SALE", 3700000000, 96.0, 4, 3, "Đông Bắc", "Sổ đỏ chính chủ", 21.3167, 105.4000, ["Gần trường cấp 3 Chuyên", "Đường 15m"]),
    ("Phú Yên", "TP. Tuy Hòa", "Phường 9", "Biệt thự nghỉ dưỡng mặt biển Rosa Alba Tuy Hòa đẳng cấp 5 sao", 3, "SALE", 11000000000, 250.0, 3, 3, "Đông", "Sổ hồng lâu dài", 13.0833, 109.3000, ["Mặt biển Tuy Hòa", "Đường hầm ra biển", "Hồ bơi riêng"]),
    ("Quảng Bình", "TP. Đồng Hới", "Bảo Ninh", "Shophouse phố đi bộ Regal Legend bán đảo Bảo Ninh view biển", 5, "SALE", 7900000000, 120.0, 4, 5, "Đông Nam", "Sổ hồng lâu dài", 17.4833, 106.6000, ["View biển Bảo Ninh", "Phố đi bộ ánh sáng", "Vật liệu chuẩn Châu Âu"]),
    ("Quảng Nam", "TP. Hội An", "Cẩm An", "Biệt thự nghỉ dưỡng phong cách Đông Dương ven sông Cổ Cò", 3, "SALE", 12500000000, 280.0, 4, 4, "Nam", "Sổ hồng riêng", 15.8833, 108.3333, ["Cách phố cổ 5 phút", "Bến thuyền ven sông", "Hồ bơi"]),
    ("Quảng Ngãi", "TP. Quảng Ngãi", "Nghĩa Chánh", "Đất nền khu đô thị Phú Mỹ Quảng Ngãi hạ tầng ngầm đồng bộ", 4, "SALE", 1850000000, 100.0, None, None, "Đông", "Sổ đỏ trao tay", 15.1167, 108.8000, ["Gần siêu thị Co.opmart", "Đường nhựa 17.5m"]),
    ("Quảng Ninh", "TP. Hạ Long", "Bãi Cháy", "Biệt thự biển Sun Grand City Feria ngắm trọn kỳ quan Vịnh Hạ Long", 3, "SALE", 26000000000, 320.0, 4, 5, "Nam", "Sổ đỏ sở hữu lâu dài", 20.9500, 107.0500, ["Tầm nhìn triệu đô vịnh di sản", "Bãi tắm riêng", "Bến du thuyền quốc tế"]),
    ("Quảng Trị", "TP. Đông Hà", "Phường 5", "Nhà phố thương mại 3 tầng đường Hùng Vương TP Đông Hà", 2, "SALE", 3300000000, 110.0, 3, 3, "Đông Nam", "Sổ đỏ chính chủ", 16.8167, 107.1000, ["Trục đường huyết mạch", "Thuận tiện kinh doanh"]),
    ("Sóc Trăng", "TP. Sóc Trăng", "Phường 3", "Nhà phố 1 trệt 2 lầu KĐT 5A thiết kế hiện đại sang trọng", 2, "SALE", 2700000000, 95.0, 3, 3, "Tây Nam", "Sổ hồng riêng", 9.6000, 105.9667, ["Khu đô thị văn minh", "Công viên cây xanh"]),
    ("Sơn La", "TP. Sơn La", "Quyết Thắng", "Nhà phố 3 tầng trung tâm thành phố Sơn La mặt đường Tô Hiệu", 2, "SALE", 3850000000, 90.0, 4, 3, "Đông Bắc", "Sổ đỏ chính chủ", 21.3269, 103.9189, ["Sổ đỏ chính chủ", "Kinh doanh đông đúc"]),
    ("Tây Ninh", "TP. Tây Ninh", "Phường 3", "Nhà phố liền kề Vincom Shophouse Tây Ninh view núi Bà Đen", 2, "SALE", 4900000000, 75.0, 4, 3, "Bắc", "Sổ hồng lâu dài", 11.3167, 106.1000, ["View núi Bà Đen", "Trung tâm thương mại Vincom"]),
    ("Thái Bình", "TP. Thái Bình", "Trần Hưng Đạo", "Liền kề KĐT Petro Thăng Long đường 20.5m hạ tầng đẹp", 2, "SALE", 3450000000, 80.0, 4, 3, "Đông", "Sổ đỏ chính chủ", 20.4500, 106.3333, ["Gần trường chuyên Thái Bình", "Dân cư đông đúc"]),
    ("Thái Nguyên", "TP. Thái Nguyên", "Phan Đình Phùng", "Căn hộ cao cấp Tecco Elite City 3PN view toàn cảnh thành phố chè", 1, "SALE", 2200000000, 81.0, 3, 2, "Đông Nam", "Sổ hồng lâu dài", 21.5833, 105.8333, ["Hồ bơi", "TTTM 3 tầng", "Vườn nướng BBQ"]),
    ("Thanh Hóa", "TP. Sầm Sơn", "Quảng Cư", "Biệt thự biển FLC Sầm Sơn Beach & Golf Resort view biển lộng gió", 3, "SALE", 14800000000, 240.0, 4, 4, "Đông", "Sổ đỏ lâu dài", 19.7500, 105.9000, ["Sân Golf 18 hố", "Hồ bơi nước mặn", "View biển"]),
    ("Thừa Thiên Huế", "TP. Huế", "Vỹ Dạ", "Biệt thự nhà vườn xứ Huế ven sông Hương thơ mộng cổ kính", 3, "SALE", 9200000000, 350.0, 4, 4, "Tây Nam", "Sổ hồng riêng", 16.4667, 107.6000, ["Ven sông Hương", "Vườn hoa cây cảnh", "Kiến trúc cung đình"]),
    ("Tiền Giang", "TP. Mỹ Tho", "Phường 1", "Nhà mặt tiền đường 30 Tháng 4 trung tâm TP Mỹ Tho sầm uất", 2, "SALE", 6200000000, 110.0, 3, 3, "Đông", "Sổ hồng hoàn công", 10.3500, 106.3667, ["Trục thương mại chính", "Gần bến tàu du lịch"]),
    ("TP. Hồ Chí Minh", "Quận 1", "Bến Nghé", "Căn hộ hàng hiệu Grand Marina Saigon Ba Son chuẩn Marriott", 1, "SALE", 18500000000, 88.0, 2, 2, "Đông Nam", "Sổ hồng sở hữu lâu dài", 10.7816, 106.7056, ["Dịch vụ quản lý Marriott", "Bến du thuyền", "View Bitexco & sông"]),
    ("Trà Vinh", "TP. Trà Vinh", "Phường 1", "Nhà riêng 2 tầng mặt tiền đường Nguyễn Đáng gần trường Đại học", 2, "SALE", 2650000000, 98.0, 3, 2, "Nam", "Sổ hồng riêng", 9.9333, 106.3333, ["Gần ĐH Trà Vinh", "Khu dân trí cao"]),
    ("Tuyên Quang", "TP. Tuyên Quang", "Tân Quang", "Shophouse Vincom Tuyên Quang ngay phố đi bộ sầm uất", 5, "SALE", 4600000000, 75.0, 4, 4, "Đông", "Sổ hồng chính chủ", 21.8167, 105.2167, ["Trung tâm lễ hội thành Tuyên", "Kinh doanh tốt"]),
    ("Vĩnh Long", "TP. Vĩnh Long", "Phường 3", "Nhà phố KĐT Minh Linh 1 trệt 2 lầu đường ô tô thông thoáng", 2, "SALE", 2750000000, 90.0, 3, 3, "Tây", "Sổ hồng riêng", 10.2500, 105.9667, ["KĐT đồng bộ", "Gần bệnh viện đa khoa"]),
    ("Vĩnh Phúc", "TP. Vĩnh Yên", "Đồng Tâm", "Biệt thự đảo Nam Đầm Vạc không gian sinh thái 4 mặt sông nước", 3, "SALE", 11500000000, 280.0, 4, 4, "Nam", "Sổ đỏ lâu dài", 21.3000, 105.5833, ["Bán đảo hồ Đầm Vạc", "Sân golf", "Bể bơi riêng"]),
    ("Yên Bái", "TP. Yên Bái", "Đồng Tâm", "Nhà phố liền kề KĐT Golden Field mặt đường đôi Điện Biên", 2, "SALE", 2950000000, 85.0, 3, 3, "Đông Nam", "Sổ đỏ chính chủ", 21.7167, 104.8833, ["KĐT hiện đại", "Hạ tầng đồng bộ", "Gần quảng trường 19/8"]),
]


def get_province_listings(seller_id: int) -> List[Dict[str, Any]]:
    """Tạo danh sách các tin đăng bao phủ 63 tỉnh/thành phố."""
    now = datetime.now(timezone.utc)
    results = []

    for idx, item in enumerate(RAW_PROVINCES):
        (
            prov,
            dist,
            ward,
            title,
            cat_id,
            t_type,
            price,
            area,
            beds,
            baths,
            direction,
            legal,
            lat,
            lng,
            features,
        ) = item

        # Chọn hình ảnh theo loại hình BĐS
        if cat_id == 1:
            imgs = UNSPLASH_APARTMENTS
        elif cat_id == 2:
            imgs = UNSPLASH_HOUSES
        elif cat_id == 3:
            imgs = UNSPLASH_VILLAS
        elif cat_id == 4:
            imgs = UNSPLASH_LAND
        else:
            imgs = UNSPLASH_COMMERCIAL

        desc = (
            f"Bất động sản chất lượng cao tại {ward}, {dist}, tỉnh {prov}. "
            f"Vị trí đắc địa, hạ tầng đồng bộ, giao thông thuận tiện. "
            f"Pháp lý: {legal}. Tiện ích ngoại khu đầy đủ gần trường học, bệnh viện, chợ và khu hành chính. "
            f"Liên hệ ngay để xem thực tế và thương lượng trực tiếp chính chủ!"
        )

        listing_dict = {
            "user_id": seller_id,
            "category_id": cat_id,
            "title": title,
            "description": desc,
            "price": price,
            "price_unit": "MONTH" if t_type == "RENT" else "TOTAL",
            "area": area,
            "bedrooms": beds,
            "bathrooms": baths,
            "direction": direction,
            "legal_status": legal,
            "address_text": f"Đường chính, {ward}, {dist}",
            "province": prov,
            "district": dist,
            "ward": ward,
            "latitude": lat,
            "longitude": lng,
            "transaction_type": t_type,
            "status": ListingStatus.APPROVED.value,
            "published_at": now - timedelta(days=(idx % 10) + 1),
            "expired_at": now + timedelta(days=30),
            "view_count": 25 + (idx * 7) % 150,
            "features": features,
            "images": imgs,
        }
        results.append(listing_dict)

    return results
