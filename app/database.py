import csv
import os
import tempfile
import threading
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

ORDER_FIELDS = [
    "order_id",
    "customer_name",
    "product_description",
    "priority",
    "status",
    "created_at",
    "updated_at",
]

ORDER_LOG_FIELDS = [
    "log_id",
    "order_id",
    "action",
    "recipient",
    "email_subject",
    "email_content",
    "status",
    "created_at",
]

_csv_lock = threading.RLock()


def _resolve_csv_path(env_key: str, default_filename: str) -> str:
    raw = os.getenv(env_key, default_filename).strip() or default_filename
    return raw if os.path.isabs(raw) else os.path.join(BASE_DIR, raw)


def get_orders_csv_path() -> str:
    return _resolve_csv_path("ORDERS_CSV_PATH", "orders_test_1000.csv")


def get_order_logs_csv_path() -> str:
    return _resolve_csv_path("ORDER_LOGS_CSV_PATH", "order_logs.csv")


def _ensure_csv_file(path: str, fieldnames: List[str]) -> None:
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()


def _read_rows(path: str, fieldnames: List[str]) -> List[Dict[str, str]]:
    _ensure_csv_file(path, fieldnames)
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def _write_rows(path: str, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", suffix=".csv", dir=directory)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _parse_order(row: Dict[str, str]) -> Dict[str, object]:
    return {
        "order_id": int(row["order_id"]),
        "customer_name": row.get("customer_name", ""),
        "product_description": row.get("product_description", ""),
        "priority": row.get("priority", "Medium"),
        "status": row.get("status", "Pending"),
        "created_at": row.get("created_at") or datetime.now().strftime(DATETIME_FMT),
        "updated_at": row.get("updated_at") or row.get("created_at") or datetime.now().strftime(DATETIME_FMT),
    }


def _parse_order_log(row: Dict[str, str]) -> Dict[str, object]:
    return {
        "log_id": int(row["log_id"]),
        "order_id": int(row["order_id"]),
        "action": row.get("action", "AUTO_EMAIL_REPLY"),
        "recipient": row.get("recipient") or None,
        "email_subject": row.get("email_subject") or None,
        "email_content": row.get("email_content", ""),
        "status": row.get("status", "SENT"),
        "created_at": row.get("created_at") or datetime.now().strftime(DATETIME_FMT),
    }


def list_orders(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, object]]:
    with _csv_lock:
        orders = [_parse_order(r) for r in _read_rows(get_orders_csv_path(), ORDER_FIELDS)]

    if priority:
        orders = [o for o in orders if o["priority"] == priority]
    if status:
        orders = [o for o in orders if o["status"] == status]
    if search and search.strip():
        kw = search.strip().lower()
        orders = [
            o
            for o in orders
            if kw in str(o["customer_name"]).lower() or kw in str(o["product_description"]).lower()
        ]

    orders.sort(key=lambda o: int(o["order_id"]), reverse=True)
    return orders


def get_order(order_id: int) -> Optional[Dict[str, object]]:
    with _csv_lock:
        for row in _read_rows(get_orders_csv_path(), ORDER_FIELDS):
            if int(row["order_id"]) == order_id:
                return _parse_order(row)
    return None


def create_order(
    customer_name: str,
    product_description: str,
    priority: str,
    status: str = "Pending",
) -> Dict[str, object]:
    now_str = datetime.now().strftime(DATETIME_FMT)
    with _csv_lock:
        path = get_orders_csv_path()
        rows = _read_rows(path, ORDER_FIELDS)
        next_id = max((int(r["order_id"]) for r in rows), default=0) + 1
        new_row = {
            "order_id": next_id,
            "customer_name": customer_name,
            "product_description": product_description,
            "priority": priority,
            "status": status,
            "created_at": now_str,
            "updated_at": now_str,
        }
        rows.append(new_row)
        _write_rows(path, ORDER_FIELDS, rows)
        return _parse_order({k: str(v) for k, v in new_row.items()})


def update_order(
    order_id: int,
    customer_name: Optional[str] = None,
    product_description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[Dict[str, object]]:
    now_str = datetime.now().strftime(DATETIME_FMT)
    with _csv_lock:
        path = get_orders_csv_path()
        rows = _read_rows(path, ORDER_FIELDS)
        updated_row = None
        for row in rows:
            if int(row["order_id"]) == order_id:
                if customer_name is not None:
                    row["customer_name"] = customer_name
                if product_description is not None:
                    row["product_description"] = product_description
                if priority is not None:
                    row["priority"] = priority
                if status is not None:
                    row["status"] = status
                row["updated_at"] = now_str
                updated_row = dict(row)
                break

        if updated_row is None:
            return None

        _write_rows(path, ORDER_FIELDS, rows)
        return _parse_order(updated_row)


def delete_order(order_id: int) -> bool:
    with _csv_lock:
        orders_path = get_orders_csv_path()
        rows = _read_rows(orders_path, ORDER_FIELDS)
        remaining = [r for r in rows if int(r["order_id"]) != order_id]
        if len(remaining) == len(rows):
            return False
        _write_rows(orders_path, ORDER_FIELDS, remaining)

        logs_path = get_order_logs_csv_path()
        if os.path.exists(logs_path):
            log_rows = _read_rows(logs_path, ORDER_LOG_FIELDS)
            remaining_logs = [r for r in log_rows if int(r["order_id"]) != order_id]
            if len(remaining_logs) != len(log_rows):
                _write_rows(logs_path, ORDER_LOG_FIELDS, remaining_logs)
        return True


def create_order_log(
    order_id: int,
    email_content: str,
    action: str = "AUTO_EMAIL_REPLY",
    recipient: Optional[str] = None,
    email_subject: Optional[str] = None,
    status: str = "SENT",
) -> Dict[str, object]:
    now_str = datetime.now().strftime(DATETIME_FMT)
    with _csv_lock:
        path = get_order_logs_csv_path()
        rows = _read_rows(path, ORDER_LOG_FIELDS)
        next_id = max((int(r["log_id"]) for r in rows), default=0) + 1
        new_row = {
            "log_id": next_id,
            "order_id": order_id,
            "action": action,
            "recipient": recipient or "",
            "email_subject": email_subject or "",
            "email_content": email_content,
            "status": status,
            "created_at": now_str,
        }
        rows.append(new_row)
        _write_rows(path, ORDER_LOG_FIELDS, rows)
        return _parse_order_log({k: str(v) for k, v in new_row.items()})


def list_order_logs(order_id: int) -> List[Dict[str, object]]:
    with _csv_lock:
        logs = [
            _parse_order_log(r)
            for r in _read_rows(get_order_logs_csv_path(), ORDER_LOG_FIELDS)
            if int(r["order_id"]) == order_id
        ]
    logs.sort(key=lambda l: int(l["log_id"]), reverse=True)
    return logs


def list_all_logs(limit: int = 50) -> List[Dict[str, object]]:
    with _csv_lock:
        logs = [_parse_order_log(r) for r in _read_rows(get_order_logs_csv_path(), ORDER_LOG_FIELDS)]
    logs.sort(key=lambda l: int(l["log_id"]), reverse=True)
    return logs[:limit]
