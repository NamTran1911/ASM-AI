import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEC_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

# Load model ML đã train từ file .pkl
try:
    import joblib
    vectorizer = joblib.load(VEC_PATH)
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Không thể load model .pkl (sẽ dùng dự đoán từ khóa cơ bản): {e}")
    vectorizer = None
    model = None


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def predict_priority(description: str) -> dict:
    cleaned = clean_text(description)

    if model is not None and vectorizer is not None:
        X = vectorizer.transform([cleaned])
        pred = model.predict(X)[0]
        confidence = 0.85
        if hasattr(model, "predict_proba"):
            confidence = float(max(model.predict_proba(X)[0]))

        return {
            "priority": str(pred),
            "confidence": round(confidence, 2),
            "description_cleaned": cleaned,
        }

    # Dự phòng đơn giản khi chưa có model .pkl
    if any(kw in cleaned for kw in ["hỏa tốc", "hoa toc", "gấp", "gap", "khẩn cấp", "khan cap", "vip"]):
        return {"priority": "High", "confidence": 0.8, "description_cleaned": cleaned}
    if any(kw in cleaned for kw in ["phụ kiện", "phu kien", "giá rẻ", "gia re", "sample", "pre order"]):
        return {"priority": "Low", "confidence": 0.75, "description_cleaned": cleaned}
    return {"priority": "Medium", "confidence": 0.7, "description_cleaned": cleaned}
