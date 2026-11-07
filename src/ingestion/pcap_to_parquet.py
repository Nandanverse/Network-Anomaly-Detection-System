import yaml
import pandas as pd
from pathlib import Path

with open("config.yaml") as f:
    config = yaml.safe_load(f)

data_dir = Path(config["paths"]["data_dir"])
zeek_log = data_dir / "flows.log"
synthetic_parquet = data_dir / "flows.parquet"
output_file = data_dir / "flows.parquet"

if zeek_log.exists():
    df = pd.read_csv(zeek_log, sep="\t", comment="#", header=None)
    df.columns = [
        "ts", "uid", "id_orig_h", "id_orig_p", "id_resp_h", "id_resp_p",
        "proto", "service", "duration", "orig_bytes", "resp_bytes",
        "conn_state", "local_orig", "local_resp", "missed_bytes",
        "history", "orig_pkts", "orig_ip_bytes", "resp_pkts", "resp_ip_bytes",
        "tunnel_parents"
    ]
    df["ts"] = pd.to_datetime(df["ts"], unit="s")
    df["duration"] = df["duration"].astype(float)
    df["label"] = "Benign"
    df["detailed_label"] = "Benign"
    df.to_parquet(output_file, index=False)
    print(f"Written {len(df)} flows from Zeek log to {output_file}")
elif synthetic_parquet.exists():
    print(f"Using existing synthetic data at {synthetic_parquet}")
else:
    raise FileNotFoundError("No Zeek log or synthetic data found. Run 'make generate-data' first.")