"""Database Seeding Script for Real Estate Platform Development

Creates initial demo categories, admin/poster users, sample listings with various statuses,
and mock buyer inquiries.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import (  # noqa: E402
    Category,
    Favorite,
    Inquiry,
    InquiryStatus,
    Listing,
    ListingFeature,
    ListingImage,
    ListingStatus,
    TransactionType,
    User,
    UserRole,
)


def seed_database():
    print("🚀 Starting database seeding...")
    db = SessionLocal()
    try:
        # 1. Categories
        categories_data = [
            ("Căn hộ chung cư", "can-ho-chung-cu", "Căn hộ cao cấp, trung cấp và nhà ở xã hội"),
            ("Nhà riêng / Nhà phố", "nha-rieng-nha-pho", "Nhà phố liền kề, nhà ngõ ngách sổ đỏ chính chủ"),
            ("Biệt thự", "biet-thu", "Biệt thự đơn lập, song lập, nhà vườn ven đô"),
            ("Đất nền dự án", "dat-nen-du-an", "Đất nền phân lô, đất đấu giá pháp lý rõ ràng"),
            ("Mặt bằng kinh doanh", "mat-bang-kinh-doanh", "Mặt bằng thương mại, shophouse cho thuê hoặc bán"),
        ]

        categories_dict = {}
        for name, slug, desc in categories_data:
            cat = db.query(Category).filter(Category.slug == slug).first()
            if not cat:
                cat = Category(name=name, slug=slug, description=desc)
                db.add(cat)
                db.flush()
                print(f"  + Added category: {name}")
            categories_dict[slug] = cat

        # 2. Users
        users_data = [
            ("admin@bds.vn", "AdminPass123!", "Quản Trị Viên Hệ Thống", "0901234567", UserRole.ADMIN.value),
            ("chutin1@bds.vn", "Password123!", "Nguyễn Văn Minh (Môi Giới)", "0912345678", UserRole.USER.value),
            ("chutin2@bds.vn", "Password123!", "Lê Hoàng Nam (Chính Chủ)", "0987654321", UserRole.USER.value),
            ("khachxem@bds.vn", "Password123!", "Trần Thu Trang (Khách Mua)", "0933445566", UserRole.USER.value),
        ]

        users_dict = {}
        for email, pwd, name, phone, role in users_data:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    password_hash=hash_password(pwd),
                    full_name=name,
                    phone_number=phone,
                    role=role,
                    is_active=True
                )
                db.add(user)
                db.flush()
                print(f"  + Added user: {email} ({role})")
            users_dict[email] = user

        now = datetime.now(timezone.utc)

        # 3. Sample Listings
        if db.query(Listing).count() == 0:
            print("  + Adding sample listings...")

            # Listing 1: Approved - Apartment in Hanoi
            l1 = Listing(
                user_id=users_dict["chutin1@bds.vn"].id,
                category_id=categories_dict["can-ho-chung-cu"].id,
                title="Bán căn hộ 2PN Vinhomes Smart City full nội thất cao cấp",
                description="Căn hộ tầng trung view công viên trung tâm cực đẹp. Diện tích thông thủy 65m2 thiết kế 2 phòng ngủ 2 vệ sinh. Đã trang bị đầy đủ nội thất cao cấp, chỉ việc xách vali vào ở. Sổ hồng chính chủ sẵn sàng giao dịch ngay.",
                transaction_type=TransactionType.SALE.value,
                price=3200000000.0,
                price_unit="TOTAL",
                area=65.0,
                bedrooms=2,
                bathrooms=2,
                direction="Đông Nam",
                legal_status="Sổ hồng lâu dài",
                address_text="Đại lộ Thăng Long, Phường Tây Mỗ",
                province="Hà Nội",
                district="Nam Từ Liêm",
                ward="Phường Tây Mỗ",
                latitude=21.0068,
                longitude=105.7441,
                status=ListingStatus.APPROVED.value,
                view_count=45,
                published_at=now - timedelta(days=2),
                expired_at=now + timedelta(days=28)
            )
            db.add(l1)
            db.flush()

            db.add_all([
                ListingFeature(listing_id=l1.id, feature_name="Sổ hồng chính chủ"),
                ListingFeature(listing_id=l1.id, feature_name="Nội thất đầy đủ"),
                ListingFeature(listing_id=l1.id, feature_name="Bể bơi 4 mùa"),
                ListingFeature(listing_id=l1.id, feature_name="Chỗ đỗ ô tô"),
                ListingImage(listing_id=l1.id, image_url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800", public_id="demo_apt_1", is_thumbnail=True, display_order=0),
                ListingImage(listing_id=l1.id, image_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800", public_id="demo_apt_2", is_thumbnail=False, display_order=1),
                ListingImage(listing_id=l1.id, image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800", public_id="demo_apt_3", is_thumbnail=False, display_order=2),
            ])

            # Listing 2: Approved - Townhouse in HCMC
            l2 = Listing(
                user_id=users_dict["chutin2@bds.vn"].id,
                category_id=categories_dict["nha-rieng-nha-pho"].id,
                title="Bán nhà phố Quận 7 vị trí đẹp mặt tiền hẻm xe hơi 6m",
                description="Nhà xây 1 trệt 2 lầu sân thượng kiên cố. Khu dân cư văn minh, an ninh tốt, gần Lotte Mart và các trường quốc tế. Diện tích 80m2, ngang 5m dài 16m, công năng đầy đủ gồm 4 phòng ngủ và 3 phòng tắm.",
                transaction_type=TransactionType.SALE.value,
                price=6800000000.0,
                price_unit="TOTAL",
                area=80.0,
                bedrooms=4,
                bathrooms=3,
                direction="Nam",
                legal_status="Sổ hồng riêng hoàn công",
                address_text="Đường Nguyễn Thị Thập",
                province="Hồ Chí Minh",
                district="Quận 7",
                ward="Phường Tân Hưng",
                latitude=10.7412,
                longitude=106.7028,
                status=ListingStatus.APPROVED.value,
                view_count=82,
                published_at=now - timedelta(days=5),
                expired_at=now + timedelta(days=25)
            )
            db.add(l2)
            db.flush()

            db.add_all([
                ListingFeature(listing_id=l2.id, feature_name="Sổ hồng riêng"),
                ListingFeature(listing_id=l2.id, feature_name="Hẻm xe hơi"),
                ListingImage(listing_id=l2.id, image_url="https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800", public_id="demo_house_1", is_thumbnail=True, display_order=0),
                ListingImage(listing_id=l2.id, image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800", public_id="demo_house_2", is_thumbnail=False, display_order=1),
                ListingImage(listing_id=l2.id, image_url="https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800", public_id="demo_house_3", is_thumbnail=False, display_order=2),
            ])

            # Listing 3: Pending Approval (for Admin testing)
            l3 = Listing(
                user_id=users_dict["chutin1@bds.vn"].id,
                category_id=categories_dict["can-ho-chung-cu"].id,
                title="Cho thuê căn hộ studio tiện nghi Cầu Giấy giá tốt",
                description="Studio diện tích 35m2 đầy đủ điều hòa, nóng lạnh, máy giặt, giường tủ. Ban công thoáng mát, bảo vệ 24/7, giờ giấc tự do không chung chủ. Phù hợp cho người đi làm hoặc sinh viên thuê dài hạn.",
                transaction_type=TransactionType.RENT.value,
                price=6500000.0,
                price_unit="MONTH",
                area=35.0,
                bedrooms=1,
                bathrooms=1,
                direction="Tây Bắc",
                legal_status="Hợp đồng thuê 1 năm",
                address_text="Số 45 Trần Thái Tông",
                province="Hà Nội",
                district="Cầu Giấy",
                ward="Phường Dịch Vọng Hậu",
                status=ListingStatus.PENDING_APPROVAL.value
            )
            db.add(l3)
            db.flush()

            db.add_all([
                ListingImage(listing_id=l3.id, image_url="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800", public_id="demo_rent_1", is_thumbnail=True, display_order=0),
                ListingImage(listing_id=l3.id, image_url="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800", public_id="demo_rent_2", is_thumbnail=False, display_order=1),
                ListingImage(listing_id=l3.id, image_url="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800", public_id="demo_rent_3", is_thumbnail=False, display_order=2),
            ])

            # Listing 4: Draft (for Poster testing)
            l4 = Listing(
                user_id=users_dict["chutin2@bds.vn"].id,
                category_id=categories_dict["dat-nen-du-an"].id,
                title="Bản nháp: Bán lô đất đấu giá Hòa Lạc tiềm năng tăng giá",
                description="Đất đấu giá diện tích 100m2 vuông vắn, đường trước mặt 12m trải nhựa. Cách khu công nghệ cao Hòa Lạc 2km. Thích hợp mua đầu tư đón sóng hạ tầng hoặc xây nhà trọ cho thuê.",
                transaction_type=TransactionType.SALE.value,
                price=2100000000.0,
                price_unit="TOTAL",
                area=100.0,
                address_text="Khu đô thị vệ tinh Hòa Lạc",
                province="Hà Nội",
                district="Thạch Thất",
                status=ListingStatus.DRAFT.value
            )
            db.add(l4)

            # 4. Mock Favorite & Inquiry
            db.flush()
            db.add(Favorite(user_id=users_dict["khachxem@bds.vn"].id, listing_id=l1.id))
            db.add(Inquiry(
                listing_id=l1.id,
                seeker_id=users_dict["khachxem@bds.vn"].id,
                sender_name="Trần Thu Trang",
                sender_phone="0933445566",
                sender_email="khachxem@bds.vn",
                message="Chào bạn, mình quan tâm căn hộ Vinhomes 2PN này. Cho mình hỏi cuối tuần này có thể qua xem thực tế được không?",
                status=InquiryStatus.NEW.value
            ))

        db.commit()
        print("✅ Database seeding completed successfully!")
    except Exception as exc:
        db.rollback()
        print(f"❌ Error during seeding: {exc}")
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
