import logging
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.chat import ChatMessage, ChatSender, ChatSession
from app.models.interaction import Favorite, Inquiry, InquiryStatus, UserViewHistory
from app.models.listing import (
    Category,
    Listing,
    ListingFeature,
    ListingImage,
    ListingModerationLog,
    ListingStatus,
    TransactionType,
)
from app.models.user import User, UserRole

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_data")


def seed_database() -> None:
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        logger.info("==================================================")
        logger.info("BẮT ĐẦU KHỞI TẠO DỮ LIỆU MẪU CHO HỆ THỐNG BDS SMART")
        logger.info("==================================================")

        # -------------------------------------------------------------
        # 1. Khởi tạo danh mục bất động sản chuẩn
        # -------------------------------------------------------------
        categories_data = [
            {"id": 1, "name": "Căn hộ chung cư", "slug": "can-ho-chung-cu", "description": "Căn hộ chung cư cao cấp, trung cấp, studio và officetel"},
            {"id": 2, "name": "Nhà riêng - Nhà phố", "slug": "nha-rieng-nha-pho", "description": "Nhà ở riêng lẻ, nhà liền kề, nhà ngõ phố và shophouse"},
            {"id": 3, "name": "Biệt thự nghỉ dưỡng", "slug": "biet-thu-nghi-duong", "description": "Biệt thự đơn lập, song lập, villa sinh thái và ven biển"},
            {"id": 4, "name": "Đất nền dự án", "slug": "dat-nen-du-an", "description": "Đất thổ cư, đất phân lô dự án và khu đô thị mới"},
            {"id": 5, "name": "Mặt bằng kinh doanh", "slug": "mat-bang-kinh-doanh", "description": "Mặt tiền buôn bán, văn phòng cho thuê và kiot thương mại"},
        ]

        for cat_info in categories_data:
            existing_cat = db.scalar(select(Category).where(Category.id == cat_info["id"]))
            if not existing_cat:
                cat = Category(
                    id=cat_info["id"],
                    name=cat_info["name"],
                    slug=cat_info["slug"],
                    description=cat_info["description"],
                )
                db.add(cat)
                logger.info(f"Đã tạo danh mục: {cat_info['name']}")
        db.commit()

        # -------------------------------------------------------------
        # 2. Khởi tạo tài khoản mẫu (Admin, Seller, Buyer)
        # -------------------------------------------------------------
        users_data = [
            {
                "email": "admin@bds-smart.vn",
                "password": "Admin@123456",
                "full_name": "Quản Trị Viên Hệ Thống",
                "phone_number": "0901234567",
                "role": UserRole.ADMIN.value,
            },
            {
                "email": "seller@bds-smart.vn",
                "password": "Seller@123456",
                "full_name": "Trần Văn Môi Giới",
                "phone_number": "0912345678",
                "role": UserRole.USER.value,
            },
            {
                "email": "buyer@bds-smart.vn",
                "password": "Buyer@123456",
                "full_name": "Lê Thị Khách Mua",
                "phone_number": "0987654321",
                "role": UserRole.USER.value,
            },
        ]

        created_users = {}
        for u in users_data:
            user = db.scalar(select(User).where(User.email == u["email"]))
            if not user:
                user = User(
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    full_name=u["full_name"],
                    phone_number=u["phone_number"],
                    role=u["role"],
                    is_active=True,
                )
                db.add(user)
                db.flush()
                logger.info(f"Đã tạo tài khoản {u['role']}: {u['email']} (Mật khẩu: {u['password']})")
            created_users[u["email"]] = user
        db.commit()

        admin_id = created_users["admin@bds-smart.vn"].id
        seller_id = created_users["seller@bds-smart.vn"].id
        buyer_id = created_users["buyer@bds-smart.vn"].id

        # -------------------------------------------------------------
        # 3. Khởi tạo danh sách bất động sản phong phú
        # -------------------------------------------------------------
        sample_listings = [
            # 1. Căn hộ Vinhomes Smart City (Approved, Sale)
            {
                "user_id": seller_id,
                "category_id": 1,
                "title": "Căn hộ cao cấp Vinhomes Smart City 2PN tầng trung ban công Đông Nam",
                "description": "Cần bán căn hộ 2 phòng ngủ 2 vệ sinh tại phân khu Sapphire Vinhomes Smart City Tây Mỗ. Căn hộ tầng 18 view hồ điều hòa thoáng mát. Nhà hoàn thiện full nội thất xịn, đồ điện tử gia dụng cao cấp chỉ việc xách vali về ở. Tiện ích nội khu đầy đủ biển nhân tạo, công viên Nhật Bản Zen Park, TTTM Vincom Mega Mall.",
                "price": 3_250_000_000,
                "price_unit": "TOTAL",
                "area": 64.5,
                "bedrooms": 2,
                "bathrooms": 2,
                "direction": "Đông Nam",
                "legal_status": "Sổ hồng lâu dài",
                "address_text": "Phân khu Sapphire, KĐT Vinhomes Smart City",
                "province": "Hà Nội",
                "district": "Nam Từ Liêm",
                "ward": "Tây Mỗ",
                "latitude": 20.9984,
                "longitude": 105.7481,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=2),
                "expired_at": now + timedelta(days=28),
                "view_count": 85,
                "features": ["Nội thất đầy đủ", "Sổ đỏ chính chủ", "Thang máy", "Bể bơi", "Gara ô tô"],
                "images": [
                    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 2. Căn hộ The Matrix One (Approved, Sale)
            {
                "user_id": seller_id,
                "category_id": 1,
                "title": "Căn hộ hạng sang The Matrix One Mễ Trì 3PN view trọn công viên 14ha",
                "description": "Chính chủ chuyển công tác cần nhượng lại căn hộ The Matrix One Mễ Trì. Thiết kế 3 phòng ngủ rộng rãi, kính Low-E tràn viền cách âm cách nhiệt tốt. Thiết bị vệ sinh Duravit, bếp Bosch nhập khẩu Đức. Tòa nhà trang bị lọc không khí và nước sạch uống tại vòi.",
                "price": 5_400_000_000,
                "price_unit": "TOTAL",
                "area": 112.0,
                "bedrooms": 3,
                "bathrooms": 2,
                "direction": "Nam",
                "legal_status": "Hợp đồng mua bán trực tiếp CĐT",
                "address_text": "Ngã tư Mễ Trì - Lê Quang Đạo",
                "province": "Hà Nội",
                "district": "Nam Từ Liêm",
                "ward": "Mễ Trì",
                "latitude": 21.0098,
                "longitude": 105.7725,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=5),
                "expired_at": now + timedelta(days=25),
                "view_count": 142,
                "features": ["Nội thất đầy đủ", "Thang máy", "Bể bơi", "Gara ô tô", "View hồ"],
                "images": [
                    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1600573472592-401b489a3cdc?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 3. Nhà phố liền kề KĐT Văn Phú (Approved, Sale)
            {
                "user_id": seller_id,
                "category_id": 2,
                "title": "Nhà phố liền kề 5 tầng KĐT Văn Phú Hà Đông đường 24m kinh doanh đỉnh",
                "description": "Bán nhà liền kề khu đô thị Văn Phú, quận Hà Đông. Diện tích 90m2 xây 5 tầng có hố chờ thang máy, mặt tiền 5m đường đôi rộng 24m vỉa hè thênh thang đỗ được 3 ô tô. Khu vực tập trung nhiều văn phòng công ty, trường học quốc tế, tiện mở spa, phòng khám hoặc cho thuê.",
                "price": 8_900_000_000,
                "price_unit": "TOTAL",
                "area": 90.0,
                "bedrooms": 5,
                "bathrooms": 5,
                "direction": "Đông Bắc",
                "legal_status": "Sổ đỏ chính chủ sẵn sàng giao dịch",
                "address_text": "Dãy TT18 KĐT Văn Phú",
                "province": "Hà Nội",
                "district": "Hà Đông",
                "ward": "Phú La",
                "latitude": 20.9632,
                "longitude": 105.7661,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=1),
                "expired_at": now + timedelta(days=29),
                "view_count": 67,
                "features": ["Sổ đỏ chính chủ", "Gara ô tô", "Thang máy"],
                "images": [
                    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 4. Căn hộ Cầu Giấy (Approved, Sale)
            {
                "user_id": seller_id,
                "category_id": 1,
                "title": "Căn hộ chung cư D'Capitale Trần Duy Hưng 2PN view hồ điều hòa Nhân Chính",
                "description": "Gia đình cần vốn kinh doanh bán gấp căn hộ D'Capitale Trần Duy Hưng, Cầu Giấy. Thiết kế 2 phòng ngủ, 2WC, phòng khách rộng mở view hồ điều hòa cực mát mẻ. Nội thất gỗ óc chó cao cấp, sàn gỗ, điều hòa âm trần Daikin. Vị trí vàng kết nối trực tiếp Trung Hòa Nhân Chính và Royal City.",
                "price": 3_950_000_000,
                "price_unit": "TOTAL",
                "area": 72.0,
                "bedrooms": 2,
                "bathrooms": 2,
                "direction": "Đông",
                "legal_status": "Sổ hồng lâu dài",
                "address_text": "119 Trần Duy Hưng",
                "province": "Hà Nội",
                "district": "Cầu Giấy",
                "ward": "Trung Hòa",
                "latitude": 21.0067,
                "longitude": 105.7958,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=3),
                "expired_at": now + timedelta(days=27),
                "view_count": 110,
                "features": ["Nội thất đầy đủ", "Sổ đỏ chính chủ", "Thang máy", "Bể bơi", "View hồ"],
                "images": [
                    "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1502005229762-ee1a681323b6?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 5. Cho thuê căn hộ Cầu Giấy (Approved, Rent)
            {
                "user_id": seller_id,
                "category_id": 1,
                "title": "Cho thuê căn hộ Discovery Complex 302 Cầu Giấy 2PN full đồ cao cấp",
                "description": "Cho thuê căn hộ Discovery Complex 302 Cầu Giấy, kết nối trực tiếp ga đường sắt trên cao Nhổn - Ga Hà Nội. Căn hộ 2 phòng ngủ tầng cao thoáng mát, đầy đủ sofa, giường nệm, TV 65 inch, máy giặt sấy. Thích hợp cho chuyên gia nước ngoài hoặc gia đình trẻ thuê ở lâu dài.",
                "price": 14_500_000,
                "price_unit": "MONTH",
                "area": 85.0,
                "bedrooms": 2,
                "bathrooms": 2,
                "direction": "Bắc",
                "legal_status": "Hợp đồng cho thuê 1 năm trở lên",
                "address_text": "302 Cầu Giấy",
                "province": "Hà Nội",
                "district": "Cầu Giấy",
                "ward": "Dịch Vọng",
                "latitude": 21.0345,
                "longitude": 105.7923,
                "transaction_type": TransactionType.RENT.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=4),
                "expired_at": now + timedelta(days=26),
                "view_count": 56,
                "features": ["Nội thất đầy đủ", "Thang máy", "Gara ô tô", "Bể bơi"],
                "images": [
                    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 6. Biệt thự đơn lập Thảo Điền TP.HCM (Approved, Sale)
            {
                "user_id": seller_id,
                "category_id": 3,
                "title": "Biệt thự đơn lập phong cách Địa Trung Hải ven sông Thảo Điền Thủ Đức",
                "description": "Bán biệt thự đơn lập sang trọng tại phường Thảo Điền, TP. Thủ Đức (Quận 2 cũ). Tổng diện tích khuôn viên 350m2, sân vườn rộng có hồ bơi tràn bờ riêng tư. Thiết kế 3 tầng phong cách Địa Trung Hải, 4 phòng ngủ master khép kín, phòng chiếu phim, hầm rượu vang và gara chứa được 2 xe hơi.",
                "price": 42_000_000_000,
                "price_unit": "TOTAL",
                "area": 350.0,
                "bedrooms": 4,
                "bathrooms": 5,
                "direction": "Tây Nam",
                "legal_status": "Sổ hồng hoàn công đầy đủ",
                "address_text": "Đường Nguyễn Văn Hưởng, Thảo Điền",
                "province": "Hồ Chí Minh",
                "district": "Thủ Đức",
                "ward": "Thảo Điền",
                "latitude": 10.8062,
                "longitude": 106.7328,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=6),
                "expired_at": now + timedelta(days=24),
                "view_count": 215,
                "features": ["Sổ đỏ chính chủ", "Gara ô tô", "Bể bơi", "Nội thất đầy đủ", "View hồ"],
                "images": [
                    "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 7. Cho thuê mặt bằng Quận 1 (Approved, Rent)
            {
                "user_id": seller_id,
                "category_id": 5,
                "title": "Cho thuê mặt bằng góc 2 mặt tiền đường Hai Bà Trưng Quận 1",
                "description": "Cho thuê nhà nguyên căn mặt tiền Hai Bà Trưng, Phường Bến Nghé, Quận 1. Vị trí đắc địa kinh doanh sầm uất ngày đêm, phù hợp mở showroom thời trang, chuỗi cafe thương hiệu lớn hoặc ngân hàng. Mặt tiền 8m ngang hiếm có, vỉa hè rộng 6m để xe thoải mái.",
                "price": 65_000_000,
                "price_unit": "MONTH",
                "area": 140.0,
                "bedrooms": 0,
                "bathrooms": 3,
                "direction": "Đông",
                "legal_status": "Hợp đồng công chứng dài hạn",
                "address_text": "Góc Hai Bà Trưng - Lê Thánh Tôn",
                "province": "Hồ Chí Minh",
                "district": "Quận 1",
                "ward": "Bến Nghé",
                "latitude": 10.7769,
                "longitude": 106.7009,
                "transaction_type": TransactionType.RENT.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=2),
                "expired_at": now + timedelta(days=28),
                "view_count": 94,
                "features": ["Gara ô tô", "Sổ đỏ chính chủ"],
                "images": [
                    "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 8. Đất nền ven biển Sơn Trà Đà Nẵng (Approved, Sale)
            {
                "user_id": seller_id,
                "category_id": 4,
                "title": "Lô đất nền thổ cư 120m2 cách bãi tắm Mỹ Khê 300m sổ đỏ vuông vắn",
                "description": "Cần bán lô đất phân lô đẹp tại quận Sơn Trà, TP. Đà Nẵng. Đường trước đất 7.5m lề mỗi bên 3m, xe du lịch tránh nhau thoải mái. Vị trí vàng cách bãi tắm Mỹ Khê chỉ 300m đi bộ, thích hợp xây khách sạn mini, căn hộ dịch vụ du lịch (homestay) thu dòng tiền cao.",
                "price": 4_600_000_000,
                "price_unit": "TOTAL",
                "area": 120.0,
                "bedrooms": 0,
                "bathrooms": 0,
                "direction": "Đông",
                "legal_status": "Sổ đỏ trao tay, đất ở đô thị 100%",
                "address_text": "Đường Võ Văn Kiệt nối dài",
                "province": "Đà Nẵng",
                "district": "Sơn Trà",
                "ward": "Phước Mỹ",
                "latitude": 16.0612,
                "longitude": 108.2435,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.APPROVED.value,
                "published_at": now - timedelta(days=7),
                "expired_at": now + timedelta(days=23),
                "view_count": 180,
                "features": ["Sổ đỏ chính chủ"],
                "images": [
                    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 9. Tin PENDING_APPROVAL dành riêng cho Kịch bản Demo Kiểm duyệt Admin
            {
                "user_id": seller_id,
                "category_id": 1,
                "title": "[CHỜ DUYỆT DEMO] Căn hộ 2PN Imperia Smart City giá tốt tầng đẹp",
                "description": "Tin đăng mới nộp duyệt dùng cho buổi bảo vệ đồ án tốt nghiệp. Căn hộ 2 phòng ngủ 1 vệ sinh tại Imperia Smart City, diện tích 55m2 bàn giao cơ bản chủ đầu tư, giá mong muốn 2.65 tỷ.",
                "price": 2_650_000_000,
                "price_unit": "TOTAL",
                "area": 55.0,
                "bedrooms": 2,
                "bathrooms": 1,
                "direction": "Đông Bắc",
                "legal_status": "Sổ hồng lâu dài",
                "address_text": "Tòa Nguyệt Quế, Imperia Smart City",
                "province": "Hà Nội",
                "district": "Nam Từ Liêm",
                "ward": "Tây Mỗ",
                "latitude": 20.9991,
                "longitude": 105.7490,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.PENDING_APPROVAL.value,
                "published_at": None,
                "expired_at": None,
                "view_count": 0,
                "features": ["Thang máy", "Bể bơi"],
                "images": [
                    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
                ],
            },
            # 10. Tin REJECTED minh họa lịch sử kiểm duyệt
            {
                "user_id": seller_id,
                "category_id": 2,
                "title": "[BỊ TỪ CHỐI DEMO] Bán nhà cấp 4 giá rẻ bất ngờ không sổ",
                "description": "Bán gấp nhà cấp 4 cũ diện tích 40m2 giá siêu rẻ tại ngõ sâu, giấy tờ viết tay mua bán vi bằng không sổ đỏ.",
                "price": 850_000_000,
                "price_unit": "TOTAL",
                "area": 40.0,
                "bedrooms": 1,
                "bathrooms": 1,
                "direction": "Tây",
                "legal_status": "Giấy viết tay",
                "address_text": "Ngõ 190 Khương Đình",
                "province": "Hà Nội",
                "district": "Thanh Xuân",
                "ward": "Khương Đình",
                "latitude": 20.9880,
                "longitude": 105.8150,
                "transaction_type": TransactionType.SALE.value,
                "status": ListingStatus.REJECTED.value,
                "published_at": None,
                "expired_at": None,
                "view_count": 0,
                "features": [],
                "images": [
                    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80",
                ],
                "moderation_reason": "Bất động sản không có giấy tờ pháp lý hợp lệ theo quy định đăng tin của sàn (yêu cầu sổ đỏ/sổ hồng hoặc HĐMB).",
            },
        ]

        seeded_listings = []
        for l_data in sample_listings:
            existing = db.scalar(select(Listing).where(Listing.title == l_data["title"]))
            if existing:
                seeded_listings.append(existing)
                continue

            moderation_reason = l_data.pop("moderation_reason", None)
            features = l_data.pop("features", [])
            images = l_data.pop("images", [])

            listing = Listing(**l_data)
            db.add(listing)
            db.flush()

            for f_name in features:
                feat = ListingFeature(listing_id=listing.id, feature_name=f_name)
                db.add(feat)

            for idx, img_url in enumerate(images):
                img = ListingImage(
                    listing_id=listing.id,
                    image_url=img_url,
                    public_id=f"demo_img_{listing.id}_{idx}",
                    is_thumbnail=(idx == 0),
                    display_order=idx,
                )
                db.add(img)

            if listing.status == ListingStatus.REJECTED.value and moderation_reason:
                mod_log = ListingModerationLog(
                    listing_id=listing.id,
                    admin_id=admin_id,
                    action="REJECT",
                    reason=moderation_reason,
                    created_at=now - timedelta(days=1),
                )
                db.add(mod_log)

            seeded_listings.append(listing)
            logger.info(f"Đã tạo tin đăng: [{listing.status}] {listing.title}")

        db.commit()

        # -------------------------------------------------------------
        # 4. Khởi tạo tương tác mẫu (Lịch sử xem, Yêu thích, Tư vấn)
        # -------------------------------------------------------------
        approved_listings = [l for l in seeded_listings if l.status == ListingStatus.APPROVED.value]

        if approved_listings:
            # Seed View History cho buyer (giúp thuật toán gợi ý cá nhân hóa hoạt động ngay)
            for l in approved_listings[:4]:
                exists_view = db.scalar(
                    select(UserViewHistory).where(
                        UserViewHistory.user_id == buyer_id,
                        UserViewHistory.listing_id == l.id,
                    )
                )
                if not exists_view:
                    view = UserViewHistory(
                        user_id=buyer_id,
                        listing_id=l.id,
                        view_duration_seconds=45,
                        created_at=now - timedelta(hours=5),
                    )
                    db.add(view)

            # Seed Favorite cho buyer
            for l in [approved_listings[0], approved_listings[1]]:
                exists_fav = db.scalar(
                    select(Favorite).where(
                        Favorite.user_id == buyer_id,
                        Favorite.listing_id == l.id,
                    )
                )
                if not exists_fav:
                    fav = Favorite(
                        user_id=buyer_id,
                        listing_id=l.id,
                        created_at=now - timedelta(hours=3),
                    )
                    db.add(fav)

            # Seed Inquiry (Yêu cầu tư vấn) gửi cho tin 1 của seller
            target_listing = approved_listings[0]
            exists_inq = db.scalar(
                select(Inquiry).where(
                    Inquiry.listing_id == target_listing.id,
                    Inquiry.user_id == buyer_id,
                )
            )
            if not exists_inq:
                inq = Inquiry(
                    listing_id=target_listing.id,
                    user_id=buyer_id,
                    full_name="Lê Thị Khách Mua",
                    phone_number="0987654321",
                    email="buyer@bds-smart.vn",
                    message="Chào bạn, tôi rất thích căn hộ Vinhomes Smart City 2PN này. Cho tôi hỏi cuối tuần này thứ Bảy lúc 9h sáng có thể đến xem trực tiếp được không?",
                    status=InquiryStatus.PENDING.value,
                    created_at=now - timedelta(hours=2),
                )
                db.add(inq)
                logger.info(f"Đã tạo yêu cầu tư vấn mẫu từ Khách mua gửi tin ID {target_listing.id}")

        db.commit()

        logger.info("==================================================")
        logger.info("KHỞI TẠO DỮ LIỆU MẪU THÀNH CÔNG RỰC RỠ!")
        logger.info("Danh sách tài khoản demo:")
        logger.info("  1. Admin  : admin@bds-smart.vn  / Admin@123456 (Quản trị & duyệt tin)")
        logger.info("  2. Seller : seller@bds-smart.vn / Seller@123456 (Đăng & quản lý tin)")
        logger.info("  3. Buyer  : buyer@bds-smart.vn  / Buyer@123456 (Khách xem, chat & lưu tin)")
        logger.info("==================================================")

    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khởi tạo dữ liệu mẫu: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
