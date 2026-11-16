"""Inference: pakai model hasil train.py untuk memprediksi data baru.

Run: python predict.py
"""
import joblib
import pandas as pd

from train import CATEGORICAL, load

bundle = joblib.load("model.joblib")
model, features = bundle["model"], bundle["features"]


def predict(rows: pd.DataFrame) -> None:
    proba = model.predict_proba(rows[features])
    classes = model.named_steps["clf"].classes_
    for (_, row), probs in zip(rows.iterrows(), proba):
        pred = classes[probs.argmax()]
        actual = row.get("label", "-")
        detail = ", ".join(f"{c}={p:.2f}" for c, p in sorted(zip(classes, probs), key=lambda x: -x[1])[:2])
        print(f"  asli={actual:<7} prediksi={pred:<7} ({detail})")


print("=== A. 5 record baru dari KDDTest+ (satu per kelas) ===")
test = load("KDDTest+.txt")
for label in ["Normal", "DoS", "Probe", "R2L", "U2R"]:
    predict(test[test["label"] == label].head(1))

print("\n=== B. input manual (dict -> satu baris) ===")
manual = {c: 0 for c in features}
manual.update({
    "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "SF",
    "src_bytes": 232, "dst_bytes": 8153, "logged_in": 1, "count": 5, "srv_count": 5,
    "same_srv_rate": 1.0, "dst_host_count": 255, "dst_host_srv_count": 255,
    "dst_host_same_srv_rate": 1.0,
})
predict(pd.DataFrame([manual]))