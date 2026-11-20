import csv
import random

# Tap du lieu mau don hang thuong mai dien tu va logistics
# Phan loai priority: High, Medium, Low dua tren mo ta san pham va yeu cau giao hang

high_templates = [
    "Giao hoa toc 2h san pham {item}, khach can gap trong buoi sang",
    "Don hang VIP: {item}, yeu cau dong goi can than, chong soc cao cap",
    "Giao gap trong ngay: {item}, khach hang dang can su dung khan cap",
    "{item} hang de vo, gia tri cao, yeu cau giao truc tiep den tay khach",
    "Don hang dac biet: {item}, phuc vu hoi nghi chieu nay, giao truoc 14h",
    "Thuoc va vat tu y te khan cap: {item}, uu tien van chuyen nhanh nhat",
    "Linh kien may chu thay the gap: {item}, he thong dang bi gian doan",
    "Thuc pham tuoi song dong lanh: {item}, can giao trong ngay tranh hu hong",
    "Banh kem sinh nhat dat truoc: {item}, giao dung gio 18h toi nay",
    "Doi tra bao hanh khan cap: {item} bi loi ky thuat, khach yeu cau doi ngay",
    "{item} nguyen seal chinh hang, don hang gia tri tren 30 trieu dong",
    "Don hang khan: {item}, yeu cau shipper lien he truoc khi giao",
    "Thiet bi y te gia dinh: {item}, giao gap cho benh nhan tai nha",
    "Tai lieu hop dong quan trong kem {item}, can chuyen phat nhanh trong 4 gio"
]

high_items = [
    "iPhone 16 Pro Max 512GB mau titan tu nhien",
    "Laptop Dell XPS 15 chuyen do hoa cao cap",
    "May anh Sony Alpha A7 IV kem ong kinh GM",
    "May tao oxy y te di dong cho nguoi gia",
    "Serum tri lieu da chuyen sau phong kham",
    "Dong ho thuy si Tissot Powermatic 80",
    "Bo vi xu ly CPU Intel Core i9 14900K",
    "Hai san King Crab tuoi song dong thung xop",
    "Banh kem sinh nhat 3 tang trang tri hoa tuoi",
    "Serum te bao goc chong lao hoa cao cap",
    "Thiet bi do dien tim di dong khan cap",
    "May chieu 4K Sony phuc vu hoi thao doanh nghiep",
    "Card man hinh RTX 4090 24GB thay the he thong render",
    "Hop sua cong thuc dac tri cho tre so sinh kem thuoc",
    "MacBook Pro 16 inch M3 Max chuyen nghiep"
]

medium_templates = [
    "Don hang tieu chuan: {item}, giao trong gio hanh chinh",
    "Mua sam gia dinh: {item}, thoi gian giao hang 2-3 ngay",
    "{item} bao hanh chinh hang 12 thang, giao tan noi",
    "Khach dat mua: {item}, phuong thuc giao hang tiet kiem",
    "Don hang online thuong: {item}, khong can giao gap",
    "Mua {item} dung trong sinh hoat hang ngay",
    "{item} chat luong tot, dong goi tieu chuan cua shop",
    "San pham thoi trang: {item}, cho phep kiem tra hang khi nhan",
    "Giao hang buu dien: {item}, nhan hang vao gio hanh chinh tai co quan",
    "Don hang tieu dung: {item}, phi ship tieu chuan",
    "Thiet bi gia dung: {item}, giao theo lich hen cuoi tuan"
]

medium_items = [
    "Noi chien khong dau Philips dung tich 6.2L",
    "Ban ui hoi nuoc cam tay Tefal cong suat lon",
    "Ao so mi nam cong so Aristino mau trang size L",
    "Giay the thao chay bo nam Nike Air Zoom Pegasus",
    "Tai nghe chup tai Sony khong day co chong on",
    "Ban phim co ban chuyen van phong Akko switch Brown",
    "Kem chong nang Anessa SPF50+ 60ml",
    "Noi com dien tu Toshiba 1.8 lit long noi gang",
    "Bo chen dia gom su Minh Long 10 mon",
    "Lo vi song Sharp co chuc nang nuong 20L",
    "May say toc ion am Panasonic 1800W",
    "Vay hoa nhi nu dang xoe chat lua thoang mat",
    "Quan jeans nam dang dung Ong suong Levis",
    "Set nuoc hoa chiet 5 chai mini bo tui",
    "Balo laptop chong nuoc Tigernu 15.6 inch",
    "Loa bluetooth mini JBL Go 3 chinh hang",
    "Gia sach go 4 tang lap ghep da nang",
    "Bo ga goi cotton Han Quoc cao cap 1m8"
]

low_templates = [
    "Don hang phu kien nho le: {item}, giao khi tien chuyen",
    "Dat truoc (Pre-order): {item}, du kien xuat kho sau 30 ngay",
    "Don hang xa kho gia re: {item}, khong can gap",
    "Mua si phu kien so luong lon: {item}, nhan hang qua xe tai vao cuoi thang",
    "Mau thu mien phi / qua tang kem: {item}, ship cham buu dien",
    "Vat tu van phong pham tieu hao: {item}, luu kho su dung dan",
    "Don hang mua thu: {item}, thoi gian van chuyen linh hoat",
    "Phu kien re tien: {item}, giao cham tiet kiem toi da cuoc van chuyen",
    "Hang dat truoc tu nuoc ngoai: {item}, cho gom chuyen phat quoc te"
]

low_items = [
    "Op lung silicon trong suot danh cho dien thoai",
    "Mieng dan cuong luc man hinh dien thoai gia re",
    "Hop 50 cay but bi Thien Long muc xanh 0.5mm",
    "Tap 100 giay note vang dan tuong tien dung",
    "Moc khoa nhua in hinh mica de thuong lam qua tang",
    "Tui zip trong suot day mieng dung linh tinh 100 chiec",
    "Set 10 kep tai nghe va day sac tien dung",
    "Goi sample mau thu sua rua mat 5ml",
    "Catalogue gioi thieu san pham mua dong 2026",
    "Day thun co gian buoc toc gia si 500 chiec",
    "Sticker nhan dan trang tri so tay mini",
    "Gia do dien thoai bang nhua mini de ban",
    "Mieng lau kinh mat chuyen dung set 5 mieng",
    "Lot chuot vai co ban size 20x25cm gia re"
]

def generate_dataset(num_samples=750, output_path="ml_training/orders_dataset.csv"):
    random.seed(42)
    records = []

    # Sinh mau cho High
    samples_per_class = num_samples // 3
    for _ in range(samples_per_class):
        tmpl = random.choice(high_templates)
        item = random.choice(high_items)
        desc = tmpl.format(item=item)
        records.append({"product_description": desc, "priority": "High"})

    # Sinh mau cho Medium
    for _ in range(samples_per_class):
        tmpl = random.choice(medium_templates)
        item = random.choice(medium_items)
        desc = tmpl.format(item=item)
        records.append({"product_description": desc, "priority": "Medium"})

    # Sinh mau cho Low
    for _ in range(samples_per_class):
        tmpl = random.choice(low_templates)
        item = random.choice(low_items)
        desc = tmpl.format(item=item)
        records.append({"product_description": desc, "priority": "Low"})

    random.shuffle(records)

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_description", "priority"])
        writer.writeheader()
        writer.writerows(records)

    print(f"Da tao {len(records)} ban ghi mau tai {output_path}")

if __name__ == "__main__":
    generate_dataset()
