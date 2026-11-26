import os
import logging
from app.database import SessionLocal
from app.models import OrderLog

logger = logging.getLogger(__name__)


def create_email_content(order_id: int, customer_name: str, product_description: str) -> str:
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()

    prompt = (
        f"Hãy viết một email ngắn gọn, lịch sự bằng tiếng Việt gửi khách hàng {customer_name}.\n"
        f"Thông báo đơn hàng #{order_id} ({product_description}) đã được xếp loại ưu tiên cao (High Priority) "
        f"và đang được xử lý giao nhanh nhất có thể."
    )

    try:
        from openai import OpenAI

        if openai_key:
            client = OpenAI(api_key=openai_key)
            res = client.chat.completions.create(
                model=model_name if "gpt" in model_name else "gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            return res.choices[0].message.content.strip()

        if gemini_key:
            client = OpenAI(
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            res = client.chat.completions.create(
                model=model_name if "gemini" in model_name else "gemini-2.5-flash-lite",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            return res.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Lỗi gọi LLM API, chuyển sang mẫu email mặc định: {e}")

    # Mẫu email mặc định khi chưa có API key
    return (
        f"Chào {customer_name},\n\n"
        f"Cảm ơn bạn đã đặt hàng! Đơn hàng #{order_id} ({product_description}) của bạn "
        f"đã được ghi nhận ở mức Ưu tiên cao (High Priority).\n"
        f"Bộ phận kho và vận chuyển đang ưu tiên đóng gói để giao đến bạn sớm nhất.\n\n"
        f"Trân trọng,\nĐội ngũ Hỗ trợ Khách hàng"
    )


def send_email_background(order_id: int, customer_name: str, product_description: str):
    logger.info(f"Bắt đầu soạn email tự động cho đơn hàng #{order_id}")
    db = SessionLocal()
    try:
        content = create_email_content(order_id, customer_name, product_description)
        log = OrderLog(
            order_id=order_id,
            action="AUTO_EMAIL_REPLY",
            recipient=customer_name,
            email_subject=f"Xác nhận ưu tiên xử lý đơn hàng #{order_id}",
            email_content=content,
            status="SENT",
        )
        db.add(log)
        db.commit()
        logger.info(f"Đã lưu log email cho đơn hàng #{order_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi lưu log email đơn #{order_id}: {e}")
    finally:
        db.close()
