#!/usr/bin/env python3
"""
Generate synthetic CICIDS2017-like flow data for testing.
Run: python scripts/generate_sample.py
Outputs: data/sample.parquet (flows) + data/sample.pcap (optional, requires scapy)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

data_dir = Path(config["paths"]["data_dir"])
data_dir.mkdir(parents=True, exist_ok=True)
np.random.seed(42)

n_benign = 50000
n_dos = 5000
n_portscan = 3000
n_bruteforce = 2000
n_webattack = 1500
n_infiltration = 1000
n_botnet = 500

def gen_benign(n):
    return pd.DataFrame({
        "ts": np.cumsum(np.random.exponential(0.1, n)) + 1700000000,
        "uid": [f"C{i:010d}" for i in range(n)],
        "id_orig_h": [f"192.168.1.{np.random.randint(2,254)}" for _ in range(n)],
        "id_orig_p": np.random.randint(1024, 65535, n),
        "id_resp_h": [f"192.168.1.{np.random.randint(2,254)}" for _ in range(n)],
        "id_resp_p": np.random.choice([80, 443, 22, 53, 25, 587, 993], n, p=[0.3,0.25,0.1,0.1,0.1,0.05,0.1]),
        "proto": np.random.choice(["tcp", "udp"], n, p=[0.85, 0.15]),
        "service": np.random.choice(["http", "ssl", "ssh", "dns", "smtp", "imap"], n, p=[0.35,0.25,0.1,0.1,0.1,0.1]),
        "duration": np.random.exponential(2.0, n),
        "orig_bytes": np.random.lognormal(6, 1.5, n).astype(int),
        "resp_bytes": np.random.lognormal(7, 1.5, n).astype(int),
        "conn_state": np.random.choice(["SF", "S0", "REJ", "RSTO"], n, p=[0.7,0.15,0.1,0.05]),
        "local_orig": True,
        "local_resp": False,
        "missed_bytes": 0,
        "history": "ShADadFf",
        "orig_pkts": np.random.poisson(15, n),
        "orig_ip_bytes": np.random.lognormal(6.5, 1.2, n).astype(int),
        "resp_pkts": np.random.poisson(12, n),
        "resp_ip_bytes": np.random.lognormal(7.5, 1.2, n).astype(int),
        "tunnel_parents": "",
        "label": "Benign",
        "detailed_label": "Benign"
    })

def gen_dos(n):
    df = gen_benign(n)
    df["label"] = "DoS"
    df["detailed_label"] = "DoS Hulk"
    df["duration"] = np.random.exponential(0.01, n)
    df["orig_bytes"] = np.random.randint(40, 100, n)
    df["resp_bytes"] = np.random.randint(40, 100, n)
    df["orig_pkts"] = np.random.randint(2, 5, n)
    df["resp_pkts"] = np.random.randint(2, 5, n)
    df["id_resp_p"] = 80
    df["service"] = "http"
    df["history"] = "S"
    return df

def gen_portscan(n):
    df = gen_benign(n)
    df["label"] = "PortScan"
    df["detailed_label"] = "PortScan"
    df["duration"] = np.random.exponential(0.001, n)
    df["orig_bytes"] = 40
    df["resp_bytes"] = 40
    df["orig_pkts"] = 1
    df["resp_pkts"] = 1
    df["conn_state"] = "S0"
    df["history"] = "S"
    df["id_resp_p"] = np.random.randint(1, 65535, n)
    return df

def gen_bruteforce(n):
    df = gen_benign(n)
    df["label"] = "BruteForce"
    df["detailed_label"] = "Web BruteForce"
    df["duration"] = np.random.exponential(5.0, n)
    df["orig_bytes"] = np.random.lognormal(5, 0.5, n).astype(int)
    df["resp_bytes"] = np.random.lognormal(6, 0.5, n).astype(int)
    df["id_resp_p"] = np.random.choice([22, 21, 23, 3389], n)
    df["service"] = np.random.choice(["ssh", "ftp", "telnet", "rdp"], n)
    df["conn_state"] = "SF"
    return df

def gen_webattack(n):
    df = gen_benign(n)
    df["label"] = "WebAttack"
    df["detailed_label"] = "SqlInjection"
    df["orig_bytes"] = np.random.lognormal(7, 1, n).astype(int)
    df["resp_bytes"] = np.random.lognormal(6, 1, n).astype(int)
    df["id_resp_p"] = np.random.choice([80, 443], n)
    df["service"] = "http"
    return df

def gen_infiltration(n):
    df = gen_benign(n)
    df["label"] = "Infiltration"
    df["detailed_label"] = "Infiltration"
    df["duration"] = np.random.exponential(30.0, n)
    df["orig_bytes"] = np.random.lognormal(8, 1.5, n).astype(int)
    df["resp_bytes"] = np.random.lognormal(6, 1.5, n).astype(int)
    df["conn_state"] = "SF"
    return df

def gen_botnet(n):
    df = gen_benign(n)
    df["label"] = "Botnet"
    df["detailed_label"] = "Botnet"
    df["duration"] = np.random.exponential(60.0, n)
    df["orig_bytes"] = np.random.lognormal(5, 1, n).astype(int)
    df["resp_bytes"] = np.random.lognormal(8, 1, n).astype(int)
    df["id_resp_p"] = np.random.randint(1024, 65535, n)
    df["conn_state"] = "SF"
    return df

print("Generating synthetic flows...")
frames = [
    gen_benign(n_benign),
    gen_dos(n_dos),
    gen_portscan(n_portscan),
    gen_bruteforce(n_bruteforce),
    gen_webattack(n_webattack),
    gen_infiltration(n_infiltration),
    gen_botnet(n_botnet)
]

df = pd.concat(frames, ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

output_file = data_dir / "flows.parquet"
df.to_parquet(output_file, index=False)
print(f"Written {len(df)} flows to {output_file}")
print(f"Label distribution:\n{df['label'].value_counts()}")

pcap_file = data_dir / "sample.pcap"
if not pcap_file.exists():
    try:
        from scapy.all import Ether, IP, TCP, UDP, Raw, wrpcap, RandShort
        print("Generating PCAP...")
        packets = []
        for _, row in df.head(10000).iterrows():
            if row["proto"] == "tcp":
                pkt = Ether()/IP(src=row["id_orig_h"], dst=row["id_resp_h"])/TCP(sport=row["id_orig_p"], dport=row["id_resp_p"])/Raw(b"X" * min(row["orig_bytes"], 1400))
            else:
                pkt = Ether()/IP(src=row["id_orig_h"], dst=row["id_resp_h"])/UDP(sport=row["id_orig_p"], dport=row["id_resp_p"])/Raw(b"X" * min(row["orig_bytes"], 1400))
            pkt.time = float(row["ts"])
            packets.append(pkt)
        wrpcap(str(pcap_file), packets)
        print(f"Written PCAP to {pcap_file}")
    except ImportError:
        print("Scapy not installed, skipping PCAP generation")

print("Done.")