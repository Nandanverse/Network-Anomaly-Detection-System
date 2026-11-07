# Run Guide — Network Anomaly Detection System

## Prerequisites (Install Before Starting)

| Tool | Required | Verify Command |
|------|----------|----------------|
| Docker Desktop | Yes | `docker --version` |
| Python 3.11+ | Yes | `python --version` |
| Git (optional) | No | `git --version` |

> **Windows:** Use **Command Prompt** or **PowerShell** (not Git Bash).

---

## Quick Start (Copy-Paste)

```cmd
cd C:\Users\nanda\OneDrive\Desktop\ids
make setup
make ingest
make features
make train
make predict
make dashboard
```

Then open:
- **Streamlit:** http://localhost:8501
- **Grafana:** http://localhost:3000 (admin/admin)

---

## Detailed Steps

### Step 1: Environment Setup
```cmd
make setup
```
- Creates `.venv/` virtual environment
- Installs all Python dependencies
- Installs pre-commit hooks
- **Time:** 30-60 sec
- **Success:** `pre-commit installed at .git/hooks/pre-commit`

---

### Step 2: Generate Data & Ingest
```cmd
make ingest
```
- Generates 63,000 synthetic flows (8 attack types)
- Runs Zeek processing (graceful fallback if no PCAP)
- Outputs `data/flows.parquet`
- **Time:** 15-30 sec
- **Success:** `Written 63000 flows from Zeek log to data\flows.parquet`

---

### Step 3: Feature Engineering
```cmd
make features
```
- Scales numerical features (StandardScaler)
- Encodes categorical features (LabelEncoder)
- Outputs `data/features.parquet`, `src/models/scaler.pkl`, `src/models/encoders.pkl`
- **Time:** 5-10 sec
- **Success:** `Features written to data\features.parquet` + `Shape: (63000, 12)`

---

### Step 4: Train Model
```cmd
make train
```
- Trains Isolation Forest (unsupervised)
- Evaluates on labeled test split
- Outputs `src/models/model.pkl`, `src/models/model_card.md`
- **Time:** 10-20 sec
- **Success:** `Metrics: {'roc_auc': 0.97..., 'precision': 0.89..., 'recall': 0.76..., 'f1': 0.82...}`

---

### Step 5: Run Predictions
```cmd
make predict
```
- Scores all flows using trained model
- Applies threshold (99th percentile)
- Outputs `data/predictions.parquet` with anomaly_score, is_anomaly, predicted_attack
- **Time:** 5 sec
- **Success:** `Total flows: 63000` + `Anomalies detected: ~630`

---

### Step 6: Launch Dashboards
```cmd
make dashboard
```
- Starts Streamlit (port 8501) + Grafana (port 3000) via Docker Compose
- **Time:** 10-15 sec (first run pulls images)
- **Success:**
  ```
  Streamlit: http://localhost:8501
  Grafana:   http://localhost:3000 (admin/admin)
  ```

---

### Step 7: Verify in Browser

| Dashboard | URL | Key Elements to Verify |
|-----------|-----|------------------------|
| Streamlit | http://localhost:8501 | 4 metric cards, timeline chart, attack breakdown bars, flow table with colored rows, MITRE ATT&CK tab |
| Grafana | http://localhost:3000 | Login admin/admin → "Network Anomaly Detection" dashboard with 6 panels (timeseries, gauges, bar, donut, table) |

---

## Expected Output Files (Confirm After Run)

```
C:\Users\nanda\OneDrive\Desktop\ids\
├── data\
│   ├── flows.parquet          ← 63k raw flows
│   ├── features.parquet       ← ML-ready features
│   └── predictions.parquet    ← Scored flows with alerts
├── src\models\
│   ├── model.pkl              ← Trained Isolation Forest
│   ├── scaler.pkl             ← StandardScaler
│   ├── encoders.pkl           ← LabelEncoders
│   └── model_card.md          ← Metrics + MITRE mapping
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `make` not recognized | Run commands manually (see below) |
| Docker permission denied | Start Docker Desktop, wait for steady whale icon |
| Port 8501/3000 in use | `make stop` then `make dashboard` |
| Streamlit shows "No data" | Run `make predict` first |
| Grafana data source error | Wait 10 sec, refresh browser |
| Python import errors | `make clean` then `make setup` |
| Any corrupted state | `make clean` then restart from Step 1 |

---

## Manual Commands (If Make Unavailable)

```cmd
# Setup
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# Pipeline
python scripts\generate_sample.py
python -m src.ingestion.pcap_to_parquet
python -m src.features.build_features
python -m src.models.train
python -m src.models.predict

# Dashboards (separate terminals)
.venv\Scripts\streamlit run dashboards\streamlit\app.py
docker compose up -d grafana
```

---

## Cleanup Commands

```cmd
make stop       # Stop dashboards
make clean      # Full reset (removes venv, data, models)
```

---

## For Full CICIDS2017 Dataset

1. Download from: `https://www.unb.ca/cic/datasets/ids-2017.html`
2. Place `.pcap` files in `data/`
3. Re-run: `make ingest` (will use real PCAP instead of synthetic)
4. Continue: `make features` → `make train` → `make predict`

---

## Support

If any step produces unexpected output, share the terminal output and I'll diagnose.