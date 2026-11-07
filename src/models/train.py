import yaml
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score,
    f1_score, average_precision_score
)
import joblib

with open("config.yaml") as f:
    config = yaml.safe_load(f)

data_dir = Path(config["paths"]["data_dir"])
model_dir = Path(config["paths"]["model_dir"])
model_dir.mkdir(parents=True, exist_ok=True)

features_file = data_dir / "features.parquet"
model_file = model_dir / "model.pkl"
card_file = model_dir / "model_card.md"

df = pd.read_parquet(features_file)

label_col = "label_encoded"
feature_cols = [c for c in df.columns if c != label_col]

X = df[feature_cols].values
y = df[label_col].values if label_col in df.columns else np.zeros(len(df))

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=config["evaluation"]["test_size"],
    stratify=y if config["evaluation"]["stratify"] else None,
    random_state=config["model"]["random_state"]
)

model = IsolationForest(
    contamination=config["model"]["contamination"],
    n_estimators=config["model"]["n_estimators"],
    max_samples=config["model"]["max_samples"],
    random_state=config["model"]["random_state"],
    n_jobs=config["model"]["n_jobs"]
)

model.fit(X_train)

scores_train = -model.score_samples(X_train)
scores_test = -model.score_samples(X_test)

threshold = np.percentile(scores_train, config["model"]["threshold_percentile"])

y_pred_train = (scores_train > threshold).astype(int)
y_pred_test = (scores_test > threshold).astype(int)

y_test_binary = (y_test != 0).astype(int)

metrics = {}
if len(np.unique(y_test_binary)) > 1:
    metrics["roc_auc"] = float(roc_auc_score(y_test_binary, scores_test))
    metrics["average_precision"] = float(average_precision_score(y_test_binary, scores_test))
    metrics["precision"] = float(precision_score(y_test_binary, y_pred_test, zero_division=0))
    metrics["recall"] = float(recall_score(y_test_binary, y_pred_test, zero_division=0))
    metrics["f1"] = float(f1_score(y_test_binary, y_pred_test, zero_division=0))

joblib.dump(model, model_file)

attack_mapping = config["features"]["attack_mapping"]
reverse_mapping = {v: k for k, v in attack_mapping.items()}

with open(card_file, "w") as f:
    f.write("# Model Card: Isolation Forest Anomaly Detector\n\n")
    f.write("## Performance (CICIDS2017 Test Split)\n\n")
    f.write("| Metric | Value |\n")
    f.write("|--------|-------|\n")
    for k, v in metrics.items():
        f.write(f"| {k} | {v:.4f} |\n")
    f.write("\n")
    f.write("## Threat Coverage (MITRE ATT&CK)\n\n")
    for tech_id, tech_name in config["mitre_attack"]["techniques"].items():
        f.write(f"- {tech_id}: {tech_name}\n")
    f.write("\n")
    f.write("## Configuration\n\n")
    f.write("```yaml\n")
    for k, v in config["model"].items():
        f.write(f"{k}: {v}\n")
    f.write("```\n")
    f.write("\n")
    f.write("## Limitations\n\n")
    f.write("- Trained on 2017 traffic patterns\n")
    f.write("- No encrypted payload inspection\n")
    f.write("- Requires retraining for new environments\n")

print(f"Model saved to {model_file}")
print(f"Model card saved to {card_file}")
print(f"Metrics: {metrics}")