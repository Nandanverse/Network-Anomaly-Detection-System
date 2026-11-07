from pathlib import Path

import joblib
import numpy as np
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

with open("config.yaml") as f:
    config = yaml.safe_load(f)

model_dir = Path(config["paths"]["model_dir"])
model = joblib.load(model_dir / "model.pkl")
scaler = joblib.load(model_dir / "scaler.pkl")
encoders = joblib.load(model_dir / "encoders.pkl")

feature_names = config["features"]["numerical"] + config["features"]["categorical"]
attack_mapping = config["features"]["attack_mapping"]
reverse_mapping = {v: k for k, v in attack_mapping.items()}
threshold = np.percentile(
    -model.score_samples(scaler.transform(np.zeros((1, len(config["features"]["numerical"]))))),
    config["model"]["threshold_percentile"],
)

app = FastAPI(title="IDS Anomaly Detection API", version="1.0.0")


class FlowInput(BaseModel):
    duration: float
    orig_bytes: float
    resp_bytes: float
    orig_pkts: float
    resp_pkts: float
    orig_ip_bytes: float
    resp_ip_bytes: float
    proto: str
    service: str
    conn_state: str
    orig_port: str
    resp_port: str


class FlowBatch(BaseModel):
    flows: list[FlowInput]


class Prediction(BaseModel):
    anomaly_score: float
    is_anomaly: int
    predicted_attack: str


class PredictionResponse(BaseModel):
    predictions: list[Prediction]


def preprocess_flow(flow: FlowInput) -> np.ndarray:
    numerical = np.array(
        [
            [
                flow.duration,
                flow.orig_bytes,
                flow.resp_bytes,
                flow.orig_pkts,
                flow.resp_pkts,
                flow.orig_ip_bytes,
                flow.resp_ip_bytes,
            ]
        ]
    )
    numerical_scaled = scaler.transform(numerical)

    categorical = np.array(
        [
            [
                (
                    encoders["proto"].transform([flow.proto])[0]
                    if flow.proto in encoders["proto"].classes_
                    else 0
                ),
                (
                    encoders["service"].transform([flow.service])[0]
                    if flow.service in encoders["service"].classes_
                    else 0
                ),
                (
                    encoders["conn_state"].transform([flow.conn_state])[0]
                    if flow.conn_state in encoders["conn_state"].classes_
                    else 0
                ),
                (
                    encoders["orig_port"].transform([flow.orig_port])[0]
                    if flow.orig_port in encoders["orig_port"].classes_
                    else 0
                ),
                (
                    encoders["resp_port"].transform([flow.resp_port])[0]
                    if flow.resp_port in encoders["resp_port"].classes_
                    else 0
                ),
            ]
        ]
    )

    return np.hstack([numerical_scaled, categorical])


@app.get("/health")
async def health():
    return {"status": "healthy", "model": "isolation_forest"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(batch: FlowBatch):
    try:
        results = []
        for flow in batch.flows:
            x = preprocess_flow(flow)
            score = -model.score_samples(x)[0]
            is_anomaly = int(score > threshold)
            predicted = reverse_mapping.get(1, "Unknown") if is_anomaly else "Benign"
            results.append(
                Prediction(
                    anomaly_score=float(score), is_anomaly=is_anomaly, predicted_attack=predicted
                )
            )
        return PredictionResponse(predictions=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/model/info")
async def model_info():
    return {
        "type": "isolation_forest",
        "features": feature_names,
        "attack_types": list(attack_mapping.keys()),
        "threshold": float(threshold),
    }
