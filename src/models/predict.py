from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

data_dir = Path(config["paths"]["data_dir"])
model_dir = Path(config["paths"]["model_dir"])

features_file = data_dir / "features.parquet"
model_file = model_dir / "model.pkl"
scaler_file = model_dir / "scaler.pkl"
output_file = data_dir / "predictions.parquet"

df = pd.read_parquet(features_file)
model = joblib.load(model_file)

feature_cols = [c for c in df.columns if c != "label_encoded"]
X = df[feature_cols].values

scores = -model.score_samples(X)
threshold = np.percentile(scores, config["model"]["threshold_percentile"])

df["anomaly_score"] = scores
df["is_anomaly"] = (scores > threshold).astype(int)

attack_mapping = config["features"]["attack_mapping"]
reverse_mapping = {v: k for k, v in attack_mapping.items()}


def map_attack(row):
    if row["is_anomaly"] == 1 and "label_encoded" in df.columns:
        return reverse_mapping.get(row["label_encoded"], "Unknown")
    return "Benign"


df["predicted_attack"] = df.apply(map_attack, axis=1)

df.to_parquet(output_file, index=False)

anomaly_count = df["is_anomaly"].sum()
print(f"Total flows: {len(df)}")
print(f"Anomalies detected: {anomaly_count}")
print(f"Predictions saved to {output_file}")