import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import SMOTE

def load_data():
    df = pd.read_csv('fraud_data.csv')
    df = df.dropna()
    df = df.drop(['nameOrig', 'nameDest', 'isFlaggedFraud'], axis=1, errors='ignore')
    df['type'] = df['type'].astype('category').cat.codes
    X = df.drop(['isFraud'], axis=1)
    y = df['isFraud']
    return train_test_split(X, y, test_size=0.2, random_state=42), X.columns

def train_model():
    (X_train, X_test, y_train, y_test), feature_names = load_data()

    # 🟡 SMOTE to balance fraud vs non-fraud
    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    model.fit(X_train_scaled, y_train)

    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    threshold = 0.2
    y_pred = (y_proba > threshold).astype(int)

    acc = accuracy_score(y_test, y_pred)

    print(f"\n✅ Model training complete and saved.\n\nAccuracy: {acc:.4f}\nThreshold: {threshold}\n")
    print("Classification Report:\n", classification_report(y_test, y_pred, zero_division=0))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("ROC-AUC Score:", roc_auc_score(y_test, y_proba))

    os.makedirs("model", exist_ok=True)
    with open("model/fraud_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("model/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("model/threshold.pkl", "wb") as f:
        pickle.dump(threshold, f)

def load_model():
    with open('model/fraud_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('model/scaler.pkl', 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    with open('model/threshold.pkl', 'rb') as threshold_file:
        threshold = pickle.load(threshold_file)
    return model, scaler, threshold

def predict_transaction(input_data):
    model, scaler, threshold = load_model()
    input_array = np.array([input_data])
    input_scaled = scaler.transform(input_array)
    proba = model.predict_proba(input_scaled)[0][1]
    is_fraud = proba > threshold
    return is_fraud, proba

if __name__ == "__main__":
    train_model()
