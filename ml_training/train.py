import os
import re
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

def clean_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s\d]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def train_order_classifier():
    data_path = "ml_training/orders_dataset.csv"
    if not os.path.exists(data_path):
        from generate_dataset import generate_dataset
        generate_dataset(output_path=data_path)

    df = pd.read_csv(data_path)
    df["clean_description"] = df["product_description"].apply(clean_text)

    X = df["clean_description"]
    y = df["priority"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Tien xu ly va vector hoa du lieu bang TF-IDF
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Thu nghiem voi 2 mo hinh: Logistic Regression va Random Forest
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    best_model_name = None
    best_accuracy = 0.0
    best_model = None
    report_content = []

    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        y_pred = model.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        matrix = confusion_matrix(y_test, y_pred, labels=["High", "Medium", "Low"])

        report_content.append(f"=== Model: {name} ===")
        report_content.append(f"Accuracy: {acc:.4f}\n")
        report_content.append("Classification Report:\n" + report)
        report_content.append(f"Confusion Matrix:\n{matrix}\n\n")

        print(f"Model {name} - Accuracy: {acc:.4f}")
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model = model

    os.makedirs("models", exist_ok=True)
    joblib.dump(vectorizer, "models/vectorizer.pkl")
    joblib.dump(best_model, "models/model.pkl")

    print(f"Chon mo hinh tot nhat: {best_model_name} voi Accuracy: {best_accuracy:.4f}")
    print("Da luu models/vectorizer.pkl va models/model.pkl")

    with open("ml_training/evaluation_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))

if __name__ == "__main__":
    train_order_classifier()
