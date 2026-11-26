import csv
import random

# Danh sách mẫu câu theo từng mức độ ưu tiên
SAMPLES = {
    "High": [
        "Giao hỏa tốc 2h {item}, khách cần gấp trong sáng nay",
        "Đơn hàng VIP: {item}, yêu cầu đóng gói chống sốc và giao ngay",
        "Đơn y tế khẩn cấp: {item}, ưu tiên chuyển nhanh nhất",
        "Hàng giá trị cao dễ vỡ: {item}, giao trực tiếp trong ngày",
        "Giao gấp trước 14h hôm nay: {item} phục vụ sự kiện",
    ],
    "Medium": [
        "Đơn hàng tiêu chuẩn: {item}, giao trong giờ hành chính",
        "Mua sắm gia đình: {item}, giao hàng 2-3 ngày",
        "{item} bảo hành 12 tháng, giao tận nơi tiết kiệm",
        "Khách đặt mua {item}, không cần giao gấp",
        "Đơn hàng online thường: {item}, phí ship tiêu chuẩn",
    ],
    "Low": [
        "Phụ kiện nhỏ lẻ: {item}, giao khi tiện chuyến",
        "Hàng đặt trước (Pre-order): {item}, giao sau 2-3 tuần",
        "Đơn hàng xả kho giá rẻ: {item}, không cần gấp",
        "Mẫu thử miễn phí / quà tặng kèm: {item}, gửi bưu điện thường",
        "Văn phòng phẩm mua trữ kho: {item}, giao chậm tiết kiệm",
    ],
}

ITEMS = {
    "High": ["iPhone 16 Pro Max", "Laptop Dell XPS 15", "Máy tạo oxy y tế", "Bánh kem sinh nhật", "Hải sản tươi sống"],
    "Medium": ["Nồi chiên không dầu Philips", "Áo sơ mi nam", "Giày chạy bộ Nike", "Tai nghe Sony", "Bộ chén dĩa Minh Long"],
    "Low": ["Ốp lưng silicon", "Miếng dán cường lực", "Bút bi Thiên Long", "Giấy note vàng", "Móc khóa nhựa"],
}


def generate_dataset(num_per_class=200, output_path="ml_training/orders_dataset.csv"):
    random.seed(42)
    rows = []

    for priority in ["High", "Medium", "Low"]:
        for _ in range(num_per_class):
            template = random.choice(SAMPLES[priority])
            item = random.choice(ITEMS[priority])
            rows.append({
                "product_description": template.format(item=item),
                "priority": priority,
            })

    random.shuffle(rows)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_description", "priority"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Đã tạo {len(rows)} mẫu dữ liệu tại {output_path}")


if __name__ == "__main__":
    generate_dataset()
