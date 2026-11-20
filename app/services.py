import logging
from openai import OpenAI
from app.config import settings
from app.database import SessionLocal
from app.models import OrderLog

logger = logging.getLogger("order_system")

def normalize_model_name(raw_name: str) -> str:
    name = raw_name.strip().lower()
    if "gemini" in name and "flash" in name and "lite" in name:
        return "gemini-2.5-flash-lite"
    if "gemini" in name and "flash" in name:
        return "gemini-2.5-flash"
    return raw_name.strip()

def get_llm_client():
    # Uu tien Google AI Studio (Gemini) theo yeu cau nguoi dung
    if settings.GEMINI_API_KEY:
        target_model = normalize_model_name(settings.LLM_MODEL)
        return OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url=settings.GEMINI_BASE_URL
        ), target_model
    
    # Fallback OpenAI neu co key
    if settings.OPENAI_API_KEY:
        return OpenAI(api_key=settings.OPENAI_API_KEY), "gpt-4o-mini"
    
    return None, None

def generate_email_draft(customer_name: str, product_description: str, order_id: int) -> str:
    client, model_name = get_llm_client()

    if client:
        try:
            prompt = (
                f"Soan mot email ngan gon, lich su va chuyen nghiep bang tieng Viet gui cho khach hang: {customer_name}.\n"
                f"Don hang ma so #{order_id} co do uu tien cao (High Priority).\n"
                f"Mo ta san pham: {product_description}.\n"
                f"Noi dung email can bao gom: loi cam on, thong bao he thong da tiep nhan va dang uu tien xu ly ngay lap tuc, "
                f"cam ket thoi gian giao hang/ho tro nhanh nhat, va thong tin lien he hotline khi can gap."
            )
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "Ban la chuyen vien cham soc khach hang cua he thong quan ly don hang."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Loi goi LLM API: {e}. Chuyen sang tao email mau du phong.")

    # Mau email du phong khi chua co API key hoac gap loi mang
    return (
        f"Kinh gui Quy khach {customer_name},\n\n"
        f"He thong xin tran trong thong bao don hang #{order_id} cua Quy khach da duoc ghi nhan voi muc do uu tien dac biet (High Priority).\n\n"
        f"Thong tin san pham: {product_description}\n"
        f"Trang thai: Dang duoc dieu phoi va chuan bi xu ly hoa toc theo quy trinh rieng.\n\n"
        f"Chuyen vien cham soc khach hang se chu dong lien he va cap nhat lo trinh den Quy khach trong thoi gian som nhat.\n\n"
        f"Tran trong cam on su tin tuong cua Quy khach!\n"
        f"Bo phan Quan ly & Xu ly Don hang."
    )

def background_email_task(order_id: int, customer_name: str, product_description: str):
    logger.info(f"Bat dau Background Task: Soan email cho don hang #{order_id} (High Priority)")
    db = SessionLocal()
    try:
        content = generate_email_draft(customer_name, product_description, order_id)
        
        log_entry = OrderLog(
            order_id=order_id,
            action="AUTO_EMAIL_REPLY",
            recipient=customer_name,
            email_subject=f"Xac nhan xu ly uu tien don hang #{order_id}",
            email_content=content,
            status="SENT"
        )
        db.add(log_entry)
        db.commit()
        logger.info(f"Hoan thanh Background Task: Da luu email vao OrderLogs cho don hang #{order_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Loi trong qua trinh thuc hien Background Task cho don hang #{order_id}: {e}")
    finally:
        db.close()
