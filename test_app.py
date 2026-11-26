from fastapi.testclient import TestClient
from app.main import app
from app.database import list_order_logs

client = TestClient(app)


def run_tests():
    # 1. Test health check
    res = client.get("/api/health")
    assert res.status_code == 200
    print("[OK] Health check:", res.json())

    # 2. Test dự đoán ML
    res_pred = client.post("/api/orders/predict", json={
        "product_description": "Giao hỏa tốc 2h laptop Dell XPS 15 khách cần gấp"
    })
    assert res_pred.status_code == 200
    print("[OK] Dự đoán AI:", res_pred.json())

    # 3. Test đọc danh sách đơn hàng từ orders_test_1000.csv
    res_list = client.get("/api/orders")
    assert res_list.status_code == 200
    initial_count = len(res_list.json())
    assert initial_count >= 1000, f"Expected >= 1000 orders, got {initial_count}"
    print(f"[OK] Đọc danh sách đơn hàng từ CSV: {initial_count} đơn")

    # 4. Test tạo đơn High Priority -> kiểm tra BackgroundTasks ghi log CSV
    res_create = client.post("/api/orders", json={
        "customer_name": "Nguyễn Văn Test",
        "product_description": "Giao gấp thiết bị y tế trong ngày",
        "priority": "High",
        "status": "Pending"
    })
    assert res_create.status_code == 201
    order_id = res_create.json()["order_id"]
    print(f"[OK] Đã tạo đơn High #{order_id}")

    logs = list_order_logs(order_id)
    assert len(logs) > 0, "Chưa có log email được tạo!"
    print(f"[OK] Background task đã lưu email: {logs[0]['email_subject']}")

    # 5. Test sửa, lọc và xóa (dọn sạch dữ liệu test)
    assert client.put(f"/api/orders/{order_id}", json={"status": "Completed"}).status_code == 200
    assert client.get(f"/api/orders/{order_id}").json()["status"] == "Completed"
    assert client.delete(f"/api/orders/{order_id}").status_code == 200
    assert len(client.get("/api/orders").json()) == initial_count
    print("[OK] CRUD đơn hàng trên CSV hoạt động bình thường")


if __name__ == "__main__":
    run_tests()
