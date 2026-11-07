import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_config_loads():
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    assert "paths" in config
    assert "model" in config
    assert "features" in config


def test_feature_columns_match_config():
    import joblib
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    model_dir = Path(config["paths"]["model_dir"])
    if not (model_dir / "scaler.pkl").exists():
        pytest.skip("Model not trained yet")

    scaler = joblib.load(model_dir / "scaler.pkl")
    encoders = joblib.load(model_dir / "encoders.pkl")

    categorical = config["features"]["categorical"]

    assert hasattr(scaler, "mean_")
    assert len(encoders) == len(categorical)


def test_model_predicts():
    import joblib
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    model_dir = Path(config["paths"]["model_dir"])
    if not (model_dir / "model.pkl").exists():
        pytest.skip("Model not trained yet")

    model = joblib.load(model_dir / "model.pkl")
    scaler = joblib.load(model_dir / "scaler.pkl")

    n_features = len(config["features"]["numerical"]) + len(config["features"]["categorical"])
    x_test = np.random.randn(10, n_features)
    x_test[:, : len(config["features"]["numerical"])] = scaler.transform(
        x_test[:, : len(config["features"]["numerical"])]
    )

    scores = -model.score_samples(x_test)
    assert scores.shape == (10,)
    assert np.all(np.isfinite(scores))


def test_predictions_file_exists():
    data_dir = Path("data")
    pred_file = data_dir / "predictions.parquet"
    if pred_file.exists():
        df = pd.read_parquet(pred_file)
        assert "anomaly_score" in df.columns
        assert "is_anomaly" in df.columns
        assert "predicted_attack" in df.columns
        assert df["is_anomaly"].isin([0, 1]).all()


def test_model_card_generated():
    model_dir = Path("src/models")
    card_file = model_dir / "model_card.md"
    if card_file.exists():
        content = card_file.read_text()
        assert "Model Card" in content
        assert "Performance" in content
        assert "MITRE ATT&CK" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
