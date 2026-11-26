import csv
import os
import random
import unicodedata
from datetime import datetime, timedelta

# Seed ngau nhien nhung co the tai lap neu can
RANDOM_SEED = 20261126

FIRST_NAMES = [
    "An", "Anh", "Bình", "Bảo", "Châu", "Chi", "Cường", "Dũng", "Dương", "Đạt",
    "Đức", "Giang", "Hà", "Hải", "Hằng", "Hạnh", "Hiếu", "Hoài", "Hoàng", "Hùng",
    "Hương", "Huy", "Huyền", "Khánh", "Khoa", "Kiên", "Lan", "Linh", "Long", "Mai",
    "Minh", "My", "Nam", "Nga", "Ngọc", "Nguyên", "Nhân", "Nhi", "Nhung", "Phong",
    "Phúc", "Phương", "Quân", "Quang", "Quỳnh", "Sơn", "Tâm", "Tân", "Thảo", "Thành",
    "Thịnh", "Thơ", "Thu", "Thủy", "Thúy", "Tiến", "Toàn", "Trang", "Trí", "Trung",
    "Trúc", "Tú", "Tuấn", "Tùng", "Tuyết", "Uyên", "Vân", "Việt", "Vinh", "Vũ", "Vy", "Yến"
]

MIDDLE_NAMES_MALE = ["Văn", "Hữu", "Đức", "Minh", "Quốc", "Anh", "Hoàng", "Thành", "Xuân", "Gia", "Bảo", "Trung"]
MIDDLE_NAMES_FEMALE = ["Thị", "Ngọc", "Minh", "Thu", "Thanh", "Phương", "Khánh", "Hoài", "Kim", "Thảo", "Bảo", "Lan"]

LAST_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Trương", "Đinh", "Mai", "Trịnh", "Đào", "Tạ"
]

ORG_CUSTOMERS = [
    "Cty TNHH Minh Phát", "Công ty CP Công nghệ Sao Việt", "Phòng khám Đa khoa An Tâm",
    "Shop Mẹ & Bé Thảo Nguyên", "Studio Ảnh Cưới Lumi", "Quán Cà Phê Góc Phố",
    "Nhà thuốc Gia Hân", "Trung tâm Anh ngữ Horizon", "Văn phòng Luật Á Đông",
    "Xưởng In Ấn Hoàng Gia", "Spa Dưỡng Sinh Hoa Sen", "Trường Mầm non Nắng Mai",
    "Cửa hàng Điện máy Tuấn Kiệt", "CLB Thể hình Titan"
]

HONORIFICS = ["Anh", "Chị", "A.", "C.", "Cô", "Chú"]
LOCATION_TAGS = ["Q1", "Q3", "Q7", "Bình Thạnh", "Tân Bình", "Gò Vấp", "Hà Đông", "Cầu Giấy", "Đống Đa", "Hải Châu"]

# Danh muc san pham theo nhom thuc te (co gia tri cao, trung binh, thap)
HIGH_TECH_ITEMS = [
    "iPhone 16 Pro Max 256GB Titan Tự Nhiên",
    "iPhone 15 Pro 128GB",
    "MacBook Air M3 13 inch 16GB/512GB",
    "MacBook Pro 14 inch M3 Pro",
    "Laptop Dell XPS 13",
    "Laptop Lenovo ThinkPad X1 Carbon",
    "Máy ảnh Sony A7 IV kèm lens 24-70mm",
    "Card màn hình RTX 4080 Super",
    "CPU Intel Core i9 14900K",
    "Màn hình Dell UltraSharp 27 inch 4K",
    "Đồng hồ Tissot Le Locle Automatic",
    "Máy chiếu 4K ViewSonic cho phòng họp",
    "Tủ lạnh Inverter Samsung 380L",
    "iPad Pro M4 11 inch WiFi"
]

HIGH_MEDICAL_ITEMS = [
    "Máy tạo oxy y tế Yuwell 5L",
    "Máy đo huyết áp bắp tay Omron HEM-7156",
    "Hộp sữa công thức NAN Optipro số 1 800g",
    "Thuốc kê đơn + vật tư thay băng y tế",
    "Máy xông khí dung Omron cho bé",
    "Bộ kit test nhanh y tế (hộp 25 test)",
    "Insulin bút tiêm bảo quản lạnh"
]

HIGH_EVENT_FOOD_ITEMS = [
    "Bánh kem sinh nhật 2 tầng mẫu hoa tươi",
    "Thùng hải sản tươi sống (tôm hùm + cua Cà Mau)",
    "Cá hồi Na Uy tươi phi lê 2kg ướp lạnh",
    "Lẵng hoa tươi khai trương kèm thiệp",
    "Nước yến sào cao cấp hộp 12 hũ làm quà biếu"
]

HIGH_VALUE_ITEMS = HIGH_TECH_ITEMS  # Alias cho borderline cases

MEDIUM_ITEMS = [
    "Nồi chiên không dầu Philips 6.2L",
    "Bàn ủi hơi nước cầm tay Tefal",
    "Áo sơ mi nam công sở Aristino size L trắng",
    "Áo polo nam vải cá sấu màu xanh navy size M",
    "Giày chạy bộ Nike Pegasus 40 size 42",
    "Giày sneaker Adidas Ultraboost trắng size 38",
    "Tai nghe Bluetooth Sony WH-CH720N đen",
    "Bàn phím cơ Akko 3087 switch Brown",
    "Chuột không dây Logitech MX Master 3S",
    "Kem chống nắng Anessa SPF50+ 60ml",
    "Nước tẩy trang Bioderma 500ml nắp hồng",
    "Nồi cơm điện tử Toshiba 1.8L",
    "Bộ chén dĩa gốm sứ Minh Long 10 món",
    "Lò vi sóng Sharp có nướng 20L",
    "Máy sấy tóc ion âm Panasonic 1800W",
    "Váy hoa nhí dáng xòe size S",
    "Quần jeans nam dáng suông Levi's size 31",
    "Balo laptop chống nước Tigernu 15.6 inch",
    "Loa Bluetooth JBL Flip 6",
    "Bộ ga gối cotton Hàn Quốc 1m8x2m",
    "Ghế công thái học văn phòng màu xám",
    "Máy lọc không khí Xiaomi Air Purifier 4",
    "Bình đun siêu tốc Lock&Lock 1.7L",
    "Sữa rửa mặt La Roche-Posay 400ml"
]

LOW_ITEMS = [
    "Ốp lưng silicon trong suốt iPhone 15",
    "Miếng dán cường lực màn hình 9D",
    "Hộp 20 cây bút bi Thiên Long mực xanh 0.5mm",
    "Xấp 5 tập giấy note vàng dán tường",
    "Móc khóa mica in hình ngẫu nhiên",
    "Túi zip trong suốt 100 chiếc size nhỏ",
    "Cáp sạc nhanh Type-C dài 1m bọc dù",
    "Gói sample kem dưỡng ẩm 5ml",
    "Tờ rơi catalogue sản phẩm mới 2026",
    "Dây buộc tóc thun co giãn túi 200 cái",
    "Sticker trang trí sổ tay (set 5 tấm)",
    "Giá đỡ điện thoại nhựa gập mini để bàn",
    "Khăn lau kính mắt chuyên dụng hộp 10 miếng",
    "Lót chuột vải size 20x25cm đen trơn",
    "Băng keo trong cuộn lớn (combo 6 cuộn)",
    "Kẹp tóc càng cua nhám Hàn Quốc",
    "Tất cổ ngắn nam cotton (set 5 đôi)",
    "Túi đựng rác tự hủy cuộn 3 cái"
]

# Cac mau cau da dang theo tung nhom ngu canh de tu nhien
HIGH_TECH_PHRASES = [
    "Giao hỏa tốc 2h {item}, khách đang cần gấp trong sáng nay",
    "Đơn VIP: {item}, đóng gói chống sốc kỹ giúp, giao tận tay khách",
    "Ship gấp trong ngày {item}, khách cần dùng liền cho kịp việc",
    "{item} - hàng dễ vỡ giá trị cao, yêu cầu shipper gọi trước khi giao",
    "Đơn đặc biệt cho hội thảo chiều nay: {item}, phải giao trước 14h",
    "Cần gấp {item}, hệ thống công ty đang gián đoạn chờ thiết bị thay thế",
    "Đổi trả bảo hành gấp: {item} khách cần nhận lại ngay trong hôm nay",
    "{item} nguyên seal chính hãng, giá trị cao, nhớ kiểm tra kỹ trước khi xuất kho",
    "Tài liệu hợp đồng gấp kèm {item}, chuyển phát nhanh trong 4h",
    "Yêu cầu xuất hóa đơn đỏ + giao hỏa tốc {item} tới văn phòng trước 16h30",
    "Đơn ưu tiên: {item}, khách quen đã chuyển khoản full, ship ngay"
]

HIGH_MEDICAL_PHRASES = [
    "Giao hỏa tốc 2h {item}, gia đình đang cần gấp cho người bệnh",
    "Đơn y tế khẩn cấp: {item}, ưu tiên chuyển ngay trong buổi sáng",
    "Khách báo hết {item}, nhờ giao sớm nhất có thể trong ngày",
    "Ship gấp {item} tới phòng khám trước 15h, gọi trước khi tới",
    "{item}, cần giữ đúng điều kiện bảo quản và giao nhanh trong 4h"
]

HIGH_EVENT_FOOD_PHRASES = [
    "{item} giao hỏa tốc trong ngày kẻo hư hỏng",
    "Đơn hẹn giờ: {item}, giao đúng 18h tối nay cho kịp tiệc",
    "Giao gấp trước 11h30 trưa nay: {item}, đóng gói cẩn thận tránh nghiêng đổ",
    "Đơn VIP: {item} gửi tặng đối tác, giao tận tay và chụp ảnh xác nhận",
    "Ship nhanh trong 2h {item}, khách cần gấp tiếp khách"
]

MEDIUM_PHRASES = [
    "Đơn tiêu chuẩn: {item}, giao giờ hành chính giúp mình",
    "Đặt mua {item}, giao hàng tiêu chuẩn 2-3 ngày là được",
    "{item} (bảo hành 12 tháng), giao tận nơi, cho kiểm hàng trước khi thanh toán",
    "Khách đặt {item}, chọn giao hàng tiết kiệm",
    "Đơn online thường: {item}, không cần giao gấp",
    "Mua {item} dùng gia đình, đóng gói cẩn thận chút nhé shop",
    "{item}, giao ở địa chỉ công ty từ thứ 2 đến thứ 6",
    "Gửi {item}, chiều mai hoặc ngày kia giao đều ok",
    "Đơn shopee/web: {item}, phí ship bình thường",
    "{item} - khách dặn cuối tuần ở nhà mới nhận được",
    "Lấy {item}, giao trước 5h chiều trong tuần này là ổn",
    "Khách hỏi mua {item}, thanh toán COD khi nhận hàng",
    "{item}, đóng gói tiêu chuẩn, gọi điện trước khi tới 15p"
]

LOW_PHRASES = [
    "Phụ kiện nhỏ: {item}, giao chung hoặc khi tiện chuyến",
    "Hàng đặt trước (pre-order): {item}, chờ đủ hàng rồi gửi",
    "Đơn xả kho giá rẻ: {item}, không gấp",
    "Mua sỉ {item} số lượng nhiều, gửi chành xe cuối tuần hoặc đầu tuần sau",
    "Quà tặng kèm / mẫu thử: {item}, đi đơn bưu điện thường",
    "Vật tư tiêu hao cho văn phòng: {item}, giao lúc nào cũng được",
    "Đơn mua thử {item}, vận chuyển chậm tiết kiệm cước",
    "Hàng gom order nước ngoài: {item}, dự kiến 2-3 tuần nữa giao",
    "Phụ kiện giá rẻ {item}, ship chậm miễn sao không thất lạc là đc",
    "Đặt thêm {item} dự phòng trong kho, tuần sau giao cũng được"
]

CASUAL_NOTES = [
    "gọi trc khi giao", "ko giao chủ nhật", "nhờ bảo vệ nhận hộ nếu ko nghe máy",
    "đã ck trước", "thu hộ COD", "đừng gọi giờ nghỉ trưa 12h-13h",
    "shipper tới cổng gọi nhé", "check kỹ màu sắc giúp", "kèm túi đựng nếu có",
    "giao đúng mẫu như hình", "khách hay bận họp, nt zalo nếu ko gọi đc"
]

BORDERLINE_DESCRIPTIONS = [
    # Truong hop mo ho hoac trai nguoc giua san pham va yeu cau giao hang
    ("Đặt {high_item}, nhưng khách đi công tác cuối tuần mới về nên tuần sau hãy giao", "Medium"),
    ("Mua {high_item} trả góp, không cần gấp, giao tiêu chuẩn 3-4 ngày", "Medium"),
    ("Đặt {low_item} gấp vì đang đi công tác quên mang theo, ship hỏa tốc tới khách sạn", "High"),
    ("Khách VIP than phiền đơn trước giao thiếu {low_item}, bù gấp trong chiều nay", "High"),
    ("{medium_item} dùng cho tiệc tối nay ở nhà hàng, nhờ giao gấp trước 17h", "High"),
    ("{medium_item}, khách cần gấp mang đi du lịch sáng mai", "High"),
    ("Combo {low_item} + {medium_item}, giao bình thường lúc nào tiện thì nhận", "Low"),
    ("{medium_item} hàng thanh lý trưng bày, khách không vội", "Low"),
    ("Đơn đặt {high_item} chờ hàng về kho cuối tháng", "Medium"),
    ("Lấy {low_item} cho sự kiện công ty sáng mai, cần giao trong tối nay", "High"),
]


def strip_accents(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def inject_realistic_imperfections(text: str, rng: random.Random) -> str:
    """Them nhieu tu nhien: viet tat, khong dau, loi go nhe, khoang trang, ghi chu doi thuong."""
    # 1. Doi luc them so luong (tranh chen vao truoc dong tu)
    if rng.random() < 0.16:
        text = text + f" (SL: {rng.randint(2, 5)})"

    # 2. Them ghi chu doi thuong cua khach
    if rng.random() < 0.25:
        note = rng.choice(CASUAL_NOTES)
        sep = rng.choice([" - ", ", ", ". Note: ", " ("])
        if sep == " (":
            text = f"{text} ({note})"
        else:
            text = f"{text}{sep}{note}"

    # 3. Thay the mot so tu thanh viet tat pho bien tai VN
    abbrev_map = [
        ("không cần", "ko cần"),
        ("không", "ko"),
        ("được", "đc"),
        ("sản phẩm", "sp"),
        ("số lượng", "sl"),
        ("văn phòng", "vp"),
        ("hóa đơn", "hđ"),
        ("trước", "trc"),
        ("chuyển khoản", "ck"),
        ("hành chính", "hc"),
        ("giờ", "h"),
    ]
    if rng.random() < 0.35:
        for full, short in abbrev_map:
            if full in text.lower() and rng.random() < 0.55:
                # Thay the khong phan biet hoa thuong don gian cho chu thuong
                text = text.replace(full, short)

    # 4. Khoang ~28% khong dau tieng Viet (nhu nguoi dung nhap nhanh hoac he thong cu)
    if rng.random() < 0.28:
        text = strip_accents(text)

    # 5. Viet thuong toan bo hoac chu dau khong viet hoa (~22%)
    r_case = rng.random()
    if r_case < 0.18:
        text = text.lower()
    elif r_case < 0.22:
        text = text[0].lower() + text[1:] if text else text

    # 6. Loi go nhe / dau cau lon xon / khoang trang thua (~15%)
    if rng.random() < 0.15:
        typo_choice = rng.random()
        if typo_choice < 0.35:
            text = text.replace(", ", "  ", 1)
        elif typo_choice < 0.65:
            text = text.replace("gấp", "gấpp").replace("gap", "gapp")
        elif typo_choice < 0.85:
            text = text + rng.choice([" !", "...", " ạ", " nha shop", " nhé"])
        else:
            # Cat bot dau cau hoac them space dau/cuoi trong qua trinh nhap
            text = " " + text.replace(":", "")

    return text


def generate_customer_name(rng: random.Random, pool: list[str]) -> str:
    # ~15% lay lai khach cu (returning customer)
    if pool and rng.random() < 0.15:
        name = rng.choice(pool)
    else:
        r = rng.random()
        if r < 0.08:
            name = rng.choice(ORG_CUSTOMERS)
        elif r < 0.16:
            # Ten kieu nhan vien nhap nhanh kem danh xung hoac khu vuc
            hon = rng.choice(HONORIFICS)
            fn = rng.choice(FIRST_NAMES)
            if rng.random() < 0.5:
                name = f"{hon} {fn} - {rng.choice(LOCATION_TAGS)}"
            else:
                name = f"{hon} {fn}"
        else:
            last = rng.choice(LAST_NAMES)
            if rng.random() < 0.5:
                mid = rng.choice(MIDDLE_NAMES_MALE)
            else:
                mid = rng.choice(MIDDLE_NAMES_FEMALE)
            first = rng.choice(FIRST_NAMES)
            # Doi khi khong co ten dem
            if rng.random() < 0.12:
                name = f"{last} {first}"
            else:
                name = f"{last} {mid} {first}"

        pool.append(name)

    # Nhieu nhe tren ten khach hang: khong dau, lowercase, ALL CAPS
    r_noise = rng.random()
    if r_noise < 0.16:
        name = strip_accents(name)
    elif r_noise < 0.22:
        name = strip_accents(name).lower()
    elif r_noise < 0.25:
        name = name.upper()

    return name


def sample_created_at(rng: random.Random, now: datetime) -> datetime:
    # Phan bo trong 90 ngay gan nhat, hoi lech ve cac ngay gan day va ngay sale (11/11, 10/10, 20/11)
    if rng.random() < 0.12:
        # Dot cao diem sale / ngay le
        spike_days = [
            datetime(2026, 11, 11),
            datetime(2026, 10, 10),
            datetime(2026, 11, 20),
            datetime(2026, 11, 25),
        ]
        base_day = rng.choice(spike_days)
    else:
        # Skew nhe ve gan hien tai
        days_ago = int((rng.random() ** 1.25) * 90)
        base_day = (now - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Gio dat don thuc te: tap trung 8h-22h, it hon vao ban dem
    if rng.random() < 0.88:
        hour = rng.randint(8, 22)
    else:
        hour = rng.choice([0, 1, 2, 3, 4, 5, 6, 7, 23])

    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    dt = base_day.replace(hour=hour, minute=minute, second=second)
    if dt > now:
        dt = now - timedelta(minutes=rng.randint(5, 180))
    return dt


def determine_status_and_updated(
    rng: random.Random, created_at: datetime, priority: str, now: datetime
) -> tuple[str, datetime]:
    age_hours = max(0.1, (now - created_at).total_seconds() / 3600.0)

    if age_hours < 6:
        status = rng.choices(["Pending", "Processing", "Completed", "Cancelled"], weights=[55, 30, 8, 7])[0]
    elif age_hours < 48:
        if priority == "High":
            status = rng.choices(["Pending", "Processing", "Completed", "Cancelled"], weights=[18, 35, 40, 7])[0]
        else:
            status = rng.choices(["Pending", "Processing", "Completed", "Cancelled"], weights=[35, 40, 15, 10])[0]
    elif age_hours < 24 * 7:
        status = rng.choices(["Pending", "Processing", "Completed", "Cancelled"], weights=[10, 22, 56, 12])[0]
    else:
        # Don cu hon 1 tuan: chu yeu da xong hoac huy, van co vai don treo
        status = rng.choices(["Pending", "Processing", "Completed", "Cancelled"], weights=[3, 5, 79, 13])[0]

    # Tinh updated_at hop ly >= created_at va <= now
    if status == "Pending":
        if rng.random() < 0.75:
            updated_at = created_at
        else:
            updated_at = created_at + timedelta(minutes=rng.randint(1, 45))
    elif status == "Processing":
        max_mins = max(5, min(int(age_hours * 60), 24 * 60))
        updated_at = created_at + timedelta(minutes=rng.randint(5, max_mins))
    elif status == "Completed":
        if priority == "High":
            max_mins = max(20, min(int(age_hours * 60), 18 * 60))
        else:
            max_mins = max(30, min(int(age_hours * 60), 96 * 60))
        updated_at = created_at + timedelta(minutes=rng.randint(15, max_mins))
    else:  # Cancelled
        max_mins = max(5, min(int(age_hours * 60), 48 * 60))
        updated_at = created_at + timedelta(minutes=rng.randint(3, max_mins))

    if updated_at > now:
        updated_at = now
    return status, updated_at


def generate_orders_csv(
    num_rows: int = 1000,
    output_path: str = "orders_test_1000.csv",
    seed: int = RANDOM_SEED,
) -> dict:
    rng = random.Random(seed)
    now = datetime(2026, 11, 26, 19, 50, 0)

    customer_pool: list[str] = []
    rows = []

    # Tao danh sach thoi gian truoc roi sap xep gan theo thu tu thoi gian (nhung van co chut xao tron nho)
    timestamps = [sample_created_at(rng, now) for _ in range(num_rows)]
    timestamps.sort()

    current_id = 1
    for i in range(num_rows):
        # ~3% nhay coc order_id (mo phong don test/nhap da bi xoa trong DB that)
        if i > 0 and rng.random() < 0.03:
            current_id += rng.choice([1, 2])
        order_id = current_id
        current_id += 1

        # ~6% ca ranh gioi / mo ho
        if rng.random() < 0.06:
            tmpl, priority = rng.choice(BORDERLINE_DESCRIPTIONS)
            raw_desc = tmpl.format(
                high_item=rng.choice(HIGH_VALUE_ITEMS),
                medium_item=rng.choice(MEDIUM_ITEMS),
                low_item=rng.choice(LOW_ITEMS),
            )
        else:
            # Phan bo lech tu nhien: ~24% High, ~51% Medium, ~25% Low
            priority = rng.choices(["High", "Medium", "Low"], weights=[24, 51, 25])[0]
            if priority == "High":
                group = rng.choices(["tech", "medical", "food"], weights=[55, 25, 20])[0]
                if group == "tech":
                    raw_desc = rng.choice(HIGH_TECH_PHRASES).format(item=rng.choice(HIGH_TECH_ITEMS))
                elif group == "medical":
                    raw_desc = rng.choice(HIGH_MEDICAL_PHRASES).format(item=rng.choice(HIGH_MEDICAL_ITEMS))
                else:
                    raw_desc = rng.choice(HIGH_EVENT_FOOD_PHRASES).format(item=rng.choice(HIGH_EVENT_FOOD_ITEMS))
            elif priority == "Medium":
                item = rng.choice(MEDIUM_ITEMS)
                # ~10% ghep 2 mon trung binh thanh 1 gio hang
                if rng.random() < 0.10:
                    item2 = rng.choice(MEDIUM_ITEMS + LOW_ITEMS)
                    item = f"{item} + {item2}"
                raw_desc = rng.choice(MEDIUM_PHRASES).format(item=item)
            else:
                item = rng.choice(LOW_ITEMS)
                if rng.random() < 0.12:
                    item2 = rng.choice(LOW_ITEMS)
                    item = f"{item}, {item2}"
                raw_desc = rng.choice(LOW_PHRASES).format(item=item)

            # ~2% nhan nhieu (mo phong nhan vien gan nham priority trong CRM thuc te)
            if rng.random() < 0.02:
                priority = rng.choice([p for p in ["High", "Medium", "Low"] if p != priority])

        desc = inject_realistic_imperfections(raw_desc, rng)
        customer_name = generate_customer_name(rng, customer_pool)
        created_at = timestamps[i]
        status, updated_at = determine_status_and_updated(rng, created_at, priority, now)

        rows.append({
            "order_id": order_id,
            "customer_name": customer_name,
            "product_description": desc,
            "priority": priority,
            "status": status,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    # Trong DB thuc te doi khi thu tu created_at hoi lech voi order_id do insert batch/async
    for idx in range(len(rows) - 1):
        if rng.random() < 0.04:
            for col in ("created_at", "updated_at", "status"):
                rows[idx][col], rows[idx + 1][col] = rows[idx + 1][col], rows[idx][col]

    fieldnames = [
        "order_id",
        "customer_name",
        "product_description",
        "priority",
        "status",
        "created_at",
        "updated_at",
    ]
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Thong ke nhanh
    prio_counts = {}
    status_counts = {}
    for r in rows:
        prio_counts[r["priority"]] = prio_counts.get(r["priority"], 0) + 1
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    return {
        "total_rows": len(rows),
        "output_path": output_path,
        "priority_counts": prio_counts,
        "status_counts": status_counts,
    }


if __name__ == "__main__":
    stats = generate_orders_csv()
    print(f"Created {stats['total_rows']} rows at {stats['output_path']}")
    print("Priority distribution:", stats["priority_counts"])
    print("Status distribution:", stats["status_counts"])
