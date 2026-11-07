from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.preprocessing import LabelEncoder, StandardScaler

with open("config.yaml") as f:
    config = yaml.safe_load(f)

data_dir = Path(config["paths"]["data_dir"])
model_dir = Path(config["paths"]["model_dir"])
input_file = data_dir / "flows.parquet"
output_file = data_dir / "features.parquet"
scaler_file = model_dir / "scaler.pkl"
encoders_file = model_dir / "encoders.pkl"

df = pd.read_parquet(input_file)

numerical = config["features"]["numerical"]
categorical = config["features"]["categorical"]
label_col = config["features"]["label_column"]

df[numerical] = df[numerical].fillna(0)
df[categorical] = df[categorical].fillna("unknown")

scaler = StandardScaler()
df[numerical] = scaler.fit_transform(df[numerical])

encoders = {}
for col in categorical:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

if label_col in df.columns:
    label_mapping = config["features"]["attack_mapping"]
    df["label_encoded"] = df[label_col].map(label_mapping).fillna(0).astype(int)

feature_cols = numerical + categorical
if "label_encoded" in df.columns:
    df[feature_cols + ["label_encoded"]].to_parquet(output_file, index=False)
else:
    df[feature_cols].to_parquet(output_file, index=False)

joblib.dump(scaler, scaler_file)
joblib.dump(encoders, encoders_file)

print(f"Features written to {output_file}")
print(f"Feature columns: {feature_cols}")
print(f"Shape: {df[feature_cols].shape}")
