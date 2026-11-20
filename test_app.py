import os
import time
import requests
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, SessionLocal
from app.models import Order, OrderLog
from app.ml import predict_order_priority

def run_tests():
    print("=== BAT DAU KIEM TRA HE THONG ===")
    
    # 1. Khoi tao DB
    init_db()
    print("[OK] Database khoi tao thanh cong.")

    client = TestClient(app)

    # 2. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check loi: {res.text}"
    health_data = res.json()
    print(f"[OK] Health check status: {health_data['status']}, ML: {health_data['ml_model']}")

    # 3. Kiem tra ML prediction
    test_cases = [
        ("Giao hoa toc 2h laptop Dell XPS 15 khan cap trong sang nay", "High"),
        ("Noi chien khong dau Philips dung tich 6L giao tieu chuan 2 ngay", "Medium"),
        ("Mieng dan cuong luc man hinh dien thoai kem sample mien phi xa kho", "Low")
    ]
    for text, expected in test_cases:
        pred = predict_order_priority(text)
        print(f"[ML Predict] '{text[:40]}...' -> {pred['priority']} (Confidence: {pred['confidence']})")
        assert pred["priority"] == expected, f"Du doan sai: mong doi {expected}, nhan duoc {pred['priority']}"
    print("[OK] ML Model du doan chinh xac cac ca test.")

    # 4. Kiem tra tao don hang voi BackgroundTasks & OrderLogs (High Priority)
    high_order_payload = {
        "customer_name": "Tran Van B",
        "product_description": "Giao hoa toc 2h thiet bi y te khan cap cho phong kham",
        "priority": "High",
        "status": "Pending"
    }
    res_high = client.post("/api/orders", json=high_order_payload)
    assert res_high.status_code == 201, f"Loi tao don hang High: {res_high.text}"
    order_data = res_high.json()
    order_id = order_data["order_id"]
    print(f"[OK] Tao thanh cong don hang High #{order_id}")

    # Kiem tra OrderLogs duoc tao boi BackgroundTasks
    db = SessionLocal()
    logs = db.query(OrderLog).filter(OrderLog.order_id == order_id).all()
    assert len(logs) > 0, "Background task chua luu email vao OrderLogs!"
    print(f"[OK] Background Task da luu email vao OrderLogs: {logs[0].email_subject}")
    print(f"     Noi dung email:\n{logs[0].email_content[:150]}...")
    db.close()

    # 5. Kiem tra tao don hang Medium (khong kich hoat auto email)
    med_order_payload = {
        "customer_name": "Le Thi C",
        "product_description": "Bo chen dia Minh Long 10 mon giao tieu chuan",
        "priority": "Medium",
        "status": "Pending"
    }
    res_med = client.post("/api/orders", json=med_order_payload)
    assert res_med.status_code == 201
    med_id = res_med.json()["order_id"]
    print(f"[OK] Tao thanh cong don hang Medium #{med_id}")

    # 6. Kiem tra lay danh sach don hang va filter
    res_list = client.get("/api/orders?priority=High")
    assert res_list.status_code == 200
    high_list = res_list.json()
    assert all(o["priority"] == "High" for o in high_list)
    print(f"[OK] Loc danh sach don hang High thanh cong ({len(high_list)} don).")

    # 7. Kiem tra cap nhat don hang
    res_update = client.put(f"/api/orders/{med_id}", json={"status": "Completed"})
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "Completed"
    print(f"[OK] Cap nhat don hang #{med_id} thanh cong.")

    # 8. Kiem tra xoa don hang
    res_del = client.delete(f"/api/orders/{med_id}")
    assert res_del.status_code == 200
    print(f"[OK] Xoa don hang #{med_id} thanh cong.")

    print("\n=== TAT CA CAC TEST DEU THANH CONG 100% ===")

if __name__ == "__main__":
    run_tests()
