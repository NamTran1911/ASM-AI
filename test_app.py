from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import OrderLog

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

    # 3. Test tạo đơn High Priority -> kiểm tra BackgroundTasks ghi OrderLog
    res_create = client.post("/api/orders", json={
        "customer_name": "Nguyễn Văn Test",
        "product_description": "Giao gấp thiết bị y tế trong ngày",
        "priority": "High",
        "status": "Pending"
    })
    assert res_create.status_code == 201
    order_id = res_create.json()["order_id"]
    print(f"[OK] Đã tạo đơn High #{order_id}")

    db = SessionLocal()
    logs = db.query(OrderLog).filter(OrderLog.order_id == order_id).all()
    assert len(logs) > 0, "Chưa có log email được tạo!"
    print(f"[OK] Background task đã lưu email: {logs[0].email_subject}")
    db.close()

    # 4. Test lấy danh sách, sửa, xóa
    assert client.get("/api/orders").status_code == 200
    assert client.put(f"/api/orders/{order_id}", json={"status": "Completed"}).status_code == 200
    assert client.delete(f"/api/orders/{order_id}").status_code == 200
    print("[OK] CRUD đơn hàng hoạt động bình thường")


if __name__ == "__main__":
    run_tests()
