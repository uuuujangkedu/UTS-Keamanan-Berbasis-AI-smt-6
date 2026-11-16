"""NSL-KDD intrusion detection: data -> EDA -> preprocessing -> training -> evaluation.

Run: python train.py
Output: data/*.txt, plots/*.png, model.joblib, metrics.csv
"""
from pathlib import Path
import urllib.request

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

BASE = Path(__file__).parent
DATA, PLOTS = BASE / "data", BASE / "plots"
SRC = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/{}"

CATEGORICAL = ["protocol_type", "service", "flag"]
COLS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty",
]

# 5 kelas: normal + 4 kategori serangan NSL-KDD
ATTACKS = {
    "DoS": ["back", "land", "neptune", "pod", "smurf", "teardrop", "mailbomb",
            "processtable", "udpstorm", "apache2", "worm"],
    "Probe": ["satan", "ipsweep", "nmap", "portsweep", "mscan", "saint"],
    "R2L": ["guess_passwd", "ftp_write", "imap", "phf", "multihop", "warezmaster",
            "warezclient", "spy", "xlock", "xsnoop", "snmpguess", "snmpgetattack",
            "httptunnel", "sendmail", "named"],
    "U2R": ["buffer_overflow", "loadmodule", "rootkit", "perl", "sqlattack",
            "xterm", "ps"],
}
LABEL_MAP = {a: cat for cat, names in ATTACKS.items() for a in names}


def load(name: str) -> pd.DataFrame:
    DATA.mkdir(exist_ok=True)
    path = DATA / name
    if not path.exists():
        print(f"Download {name} ...")
        urllib.request.urlretrieve(SRC.format(name), path)
    df = pd.read_csv(path, names=COLS, index_col=False)
    df["label"] = df["label"].str.strip().map(lambda x: LABEL_MAP.get(x, "Normal"))
    return df


def eda(train: pd.DataFrame) -> list[str]:
    PLOTS.mkdir(exist_ok=True)
    print("\n=== 1. DATA ===")
    print(f"shape: {train.shape}")
    print(f"missing: {int(train.isna().sum().sum())}")
    print("\n5 baris pertama:")
    print(train.head(5).to_string(max_cols=10))
    print("\ntipe kolom kategorikal:", train[CATEGORICAL].dtypes.to_dict())
    print("\ndistribusi kelas:")
    print(train["label"].value_counts().to_string())
    print("\ntop 10 service:")
    print(train["service"].value_counts().head(10).to_string())

    counts = train["label"].value_counts()
    ax = counts.plot.bar(color="#2b6cb0", figsize=(7, 4))
    ax.set_title("Distribusi kelas (imbalance)")
    ax.set_ylabel("jumlah record")
    for i, v in enumerate(counts.values):
        ax.text(i, v, f"{v}\n({v/len(train):.1%})", ha="center", va="bottom", fontsize=8)
    ax.figure.tight_layout()
    ax.figure.savefig(PLOTS / "01_class_distribution.png", dpi=150)
    plt.close(ax.figure)

    numeric = train.drop(columns=CATEGORICAL + ["label", "difficulty"])
    corr = numeric.corr()
    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=90, fontsize=6)
    ax.set_yticks(range(len(corr)), corr.columns, fontsize=6)
    ax.set_title("Korelasi fitur numerik")
    fig.colorbar(im, fraction=0.04)
    fig.tight_layout()
    fig.savefig(PLOTS / "02_correlation.png", dpi=150)
    plt.close(fig)

    cat = train.groupby(["label", "protocol_type"]).size().unstack(fill_value=0)
    ax = cat.plot.bar(stacked=True, figsize=(8, 4))
    ax.set_title("Kelas x protocol_type")
    ax.figure.tight_layout()
    ax.figure.savefig(PLOTS / "03_protocol.png", dpi=150)
    plt.close(ax.figure)

    # kolom konstan = tidak informatif
    constant = [c for c in numeric if numeric[c].nunique() == 1]
    print(f"\nkolom konstan (dibuang): {constant}")
    return constant


def build(train: pd.DataFrame, constant: list[str]) -> tuple[list[str], ColumnTransformer]:
    features = [c for c in COLS if c not in ("label", "difficulty") and c not in constant]
    prep = ColumnTransformer([
        ("num", StandardScaler(), [c for c in features if c not in CATEGORICAL]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    return features, prep


def main() -> None:
    train_df, test_df = load("KDDTrain+.txt"), load("KDDTest+.txt")
    constant = eda(train_df)
    features, prep = build(train_df, constant)
    X_train, y_train = train_df[features], train_df["label"]
    X_test, y_test = test_df[features], test_df["label"]

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=150, class_weight="balanced", n_jobs=-1, random_state=42
        ),
        "DecisionTree": DecisionTreeClassifier(class_weight="balanced", random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=2000),
    }

    print("\n=== 2. TRAINING & EVALUASI ===")
    rows, best = [], None
    for name, clf in models.items():
        pipe = Pipeline([("prep", prep), ("clf", clf)]).fit(X_train, y_train)
        pred = pipe.predict(X_test)
        macro = f1_score(y_test, pred, average="macro")
        acc = (pred == y_test).mean()
        rows.append({"model": name, "accuracy": round(acc, 4), "f1_macro": round(macro, 4)})
        print(f"\n--- {name} (accuracy={acc:.4f}, f1_macro={macro:.4f}) ---")
        print(classification_report(y_test, pred, digits=3))
        if name == "RandomForest":
            best = (pipe, pred)

    print("\n=== 3. PERBANDINGAN MODEL ===")
    print(pd.DataFrame(rows).to_string(index=False))
    pd.DataFrame(rows).to_csv(BASE / "metrics.csv", index=False)

    pipe, pred = best
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax, cmap="Blues", xticks_rotation=45)
    ax.set_title("Confusion matrix - RandomForest")
    fig.tight_layout()
    fig.savefig(PLOTS / "04_confusion_matrix.png", dpi=150)
    plt.close(fig)

    names = pipe.named_steps["prep"].get_feature_names_out()
    imp = pd.Series(pipe.named_steps["clf"].feature_importances_, index=names).nlargest(15)
    ax = imp[::-1].plot.barh(figsize=(8, 6), color="#2b6cb0")
    ax.set_title("15 fitur paling penting")
    ax.figure.tight_layout()
    ax.figure.savefig(PLOTS / "05_feature_importance.png", dpi=150)
    plt.close(ax.figure)

    joblib.dump({"model": pipe, "features": features}, BASE / "model.joblib")
    print("\nmodel disimpan: model.joblib | plot: plots/ | metrik: metrics.csv")


if __name__ == "__main__":
    main()