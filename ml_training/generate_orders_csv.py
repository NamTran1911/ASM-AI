import csv
import random
from datetime import datetime, timedelta
from generate_dataset import SAMPLES, ITEMS

CUSTOMERS = [
    "Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường", "Phạm Minh Dũng",
    "Hoàng Lan Anh", "Vũ Quốc Bảo", "Đặng Thu Hà", "Bùi Đức Huy",
]
STATUSES = ["Pending", "Processing", "Completed", "Cancelled"]


def generate_test_orders(total=1000, output_path="orders_test_1000.csv"):
    random.seed(42)
    start_time = datetime(2026, 8, 29, 8, 0, 0)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "customer_name", "product_description", "priority", "status", "created_at", "updated_at"])

        for i in range(1, total + 1):
            priority = random.choice(["High", "Medium", "Low"])
            desc = random.choice(SAMPLES[priority]).format(item=random.choice(ITEMS[priority]))
            created = start_time + timedelta(hours=i)
            updated = created + timedelta(hours=random.randint(1, 24))
            writer.writerow([
                i,
                random.choice(CUSTOMERS),
                desc,
                priority,
                random.choice(STATUSES),
                created.strftime("%Y-%m-%d %H:%M:%S"),
                updated.strftime("%Y-%m-%d %H:%M:%S"),
            ])

    print(f"Đã tạo {total} đơn hàng mẫu tại {output_path}")


if __name__ == "__main__":
    generate_test_orders()
