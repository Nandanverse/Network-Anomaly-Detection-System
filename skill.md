# Network Anomaly Detection — Skill Reference

## Project Overview
Real-time network traffic anomaly detection using Isolation Forest on Zeek-extracted flow features. Maps anomalies to MITRE ATT&CK techniques. Runs entirely locally via Docker Compose.

## Commands

### Setup
```bash
make setup          # Create venv, install deps, install pre-commit hooks
```

### Data Pipeline
```bash
make ingest         # Download sample PCAP, run Zeek, convert to Parquet
make features       # Build ML features (scaling + encoding)
```

### Model Training
```bash
make train          # Train Isolation Forest, generate model_card.md
make predict        # Run inference, produce predictions.parquet
```

### Visualization
```bash
make dashboard      # Start Streamlit (8501) + Grafana (3000)
make logs           # Follow Docker logs
make stop           # Stop all containers
```

### Quality
```bash
make test           # Run pytest suite
make lint           # Run ruff + black checks
make format         # Auto-fix formatting
```

### Full Pipeline
```bash
make full           # setup -> ingest -> features -> train -> dashboard
make clean          # Remove venv, generated data, models
```

## Architecture

```
PCAP → Zeek → flows.log → Parquet → Features → Isolation Forest → Predictions
                                                      ↓
                                    Streamlit Dashboard + Grafana
                                                      ↓
                                            MITRE ATT&CK Mapping
```

## Key Files

| File | Purpose |
|------|---------|
| `config.yaml` | All hyperparameters, paths, attack mappings |
| `docker-compose.yml` | Zeek, Streamlit, Grafana, DuckDB services |
| `src/ingestion/zeek_scripts/extract_flows.zeek` | Custom Zeek flow extraction |
| `src/models/train.py` | Isolation Forest training + evaluation |
| `src/models/predict.py` | Batch inference on feature matrix |
| `dashboards/streamlit/app.py` | Real-time alert dashboard |
| `dashboards/grafana/ids.json` | Pre-built Grafana dashboard |
| `src/api/main.py` | FastAPI model serving endpoint |

## Model Card
Generated at `src/models/model_card.md` after training. Contains:
- ROC-AUC, Precision, Recall, F1, Average Precision
- MITRE ATT&CK technique coverage table
- Configuration snapshot
- Known limitations

## Attack Type Mapping (config.yaml)
| Label | Code | MITRE Technique |
|-------|------|-----------------|
| Benign | 0 | — |
| DoS | 1 | T1499 |
| DDoS | 2 | T1498 |
| PortScan | 3 | T1046 |
| BruteForce | 4 | T1110 |
| WebAttack | 5 | T1190 |
| Infiltration | 6 | T1059 |
| Botnet | 7 | T1071, T1041 |

## Extending

### Add New Attack Type
1. Add to `config.yaml` → `features.attack_mapping`
2. Add MITRE technique to `config.yaml` → `mitre_attack.techniques`
3. Add color to `config.yaml` → `dashboard.attack_colors`
4. Retrain: `make train`

### Add New Feature
1. Modify Zeek script to extract field
2. Add to `config.yaml` → `features.numerical` or `categorical`
3. Rebuild: `make features && make train`

### Swap Model
Replace `src/models/train.py` model instantiation. Keep same interface:
- `fit(X_train)`
- `score_samples(X)` → anomaly scores (higher = more anomalous)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Zeek fails | `docker compose logs zeek` — check PCAP format |
| No anomalies | Lower `model.contamination` or `model.threshold_percentile` |
| Dashboard empty | Run `make predict` first |
| Port conflict | Change ports in `config.yaml` and `docker-compose.yml` |
| Memory error | Reduce `model.n_estimators` or `model.max_samples` |

## Data Sources
- **Sample**: 50MB CICIDS2017 slice (auto-downloaded)
- **Full**: CICIDS2017 (3GB), UNSW-NB15 (5GB), CSE-CIC-IDS2018 (20GB)
- Download scripts in `scripts/` (create as needed)

## Performance Baselines (CICIDS2017)
| Metric | Target |
|--------|--------|
| ROC-AUC | > 0.95 |
| Precision@1% | > 0.85 |
| Recall@1% | > 0.70 |
| Inference latency | < 5ms/flow |

## License
MIT — Free for academic and commercial use.