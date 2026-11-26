import os
import re
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


def clean_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def train():
    data_path = "ml_training/orders_dataset.csv"
    df = pd.read_csv(data_path)
    df["clean_text"] = df["product_description"].apply(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df["priority"], test_size=0.2, random_state=42
    )

    # Vector hóa văn bản bằng TF-IDF
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Huấn luyện model Logistic Regression
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_vec, y_train)

    # Đánh giá model
    y_pred = model.predict(X_test_vec)
    print(f"Độ chính xác (Accuracy): {accuracy_score(y_test, y_pred):.2%}")
    print(classification_report(y_test, y_pred))

    # Lưu vectorizer và model ra file .pkl
    os.makedirs("models", exist_ok=True)
    joblib.dump(vectorizer, "models/vectorizer.pkl")
    joblib.dump(model, "models/model.pkl")
    print("Đã lưu models/vectorizer.pkl và models/model.pkl")


if __name__ == "__main__":
    train()
