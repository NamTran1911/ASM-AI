import os
import re
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
VEC_PATH = os.path.join(MODELS_DIR, "vectorizer.pkl")
MODEL_PATH = os.path.join(MODELS_DIR, "model.pkl")

vectorizer = None
model = None

def load_ml_components():
    global vectorizer, model
    if os.path.exists(VEC_PATH) and os.path.exists(MODEL_PATH):
        try:
            vectorizer = joblib.load(VEC_PATH)
            model = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Loi khi load model .pkl: {e}")
            vectorizer = None
            model = None

load_ml_components()

def clean_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s\d]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def predict_order_priority(description: str) -> dict:
    global vectorizer, model
    if vectorizer is None or model is None:
        load_ml_components()

    cleaned = clean_text(description)

    # Neu da load duoc model scikit-learn tu .pkl
    if vectorizer is not None and model is not None:
        vec = vectorizer.transform([cleaned])
        pred = model.predict(vec)[0]
        
        # Lay do tin cay confidence neu model ho tro predict_proba
        confidence = 0.85
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(vec)[0]
            confidence = float(max(probs))

        return {
            "priority": str(pred),
            "confidence": round(confidence, 4),
            "description_cleaned": cleaned
        }

    # Fallback don gian neu chua co file pkl
    low_keywords = ["phu kien", "gia re", "tang kem", "sample", "mau thu", "xa kho", "pre order"]
    high_keywords = ["hoa toc", "gap", "khan cap", "vip", "de vo", "iphone", "laptop", "y te"]

    for kw in high_keywords:
        if kw in cleaned:
            return {"priority": "High", "confidence": 0.8, "description_cleaned": cleaned}

    for kw in low_keywords:
        if kw in cleaned:
            return {"priority": "Low", "confidence": 0.75, "description_cleaned": cleaned}

    return {"priority": "Medium", "confidence": 0.7, "description_cleaned": cleaned}
