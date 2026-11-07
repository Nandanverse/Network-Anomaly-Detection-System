#!/usr/bin/env python3
"""Generate representative dashboard screenshots for documentation."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path

output_dir = Path("docs/images")
output_dir.mkdir(parents=True, exist_ok=True)

# Color scheme matching the project
COLORS = {
    "benign": "#2e7d32",
    "anomaly": "#c62828",
    "dos": "#c62828",
    "ddos": "#b71c1c",
    "portscan": "#ef6c00",
    "bruteforce": "#d84315",
    "webattack": "#ad1457",
    "infiltration": "#6a1b9a",
    "botnet": "#4a148c",
    "primary": "#2c3e50",
    "bg": "#ffffff",
    "grid": "#e8e8e8",
    "text": "#1a1a2e",
    "text_secondary": "#4a4a6a",
}

# ------------------------------------------------------------------
# 1. Streamlit Dashboard - Main View
# ------------------------------------------------------------------
fig = go.Figure()

# Generate sample timeline data
np.random.seed(42)
times = pd.date_range("2026-11-07 10:00", periods=60, freq="1min")
benign = np.random.poisson(800, 60) + 200
anomalies = np.zeros(60)
anomalies[15:20] = np.random.poisson(30, 5)
anomalies[35:40] = np.random.poisson(45, 5)
anomalies[50:55] = np.random.poisson(25, 5)

fig.add_trace(go.Scatter(
    x=times, y=benign,
    name="Benign", mode="lines",
    line=dict(color=COLORS["benign"], width=2),
    fill="tozeroy", fillcolor="rgba(46, 125, 50, 0.1)",
    hovertemplate="%{y} flows<extra></extra>"
))
fig.add_trace(go.Scatter(
    x=times, y=anomalies,
    name="Anomalies", mode="lines",
    line=dict(color=COLORS["anomaly"], width=2),
    fill="tozeroy", fillcolor="rgba(198, 40, 40, 0.1)",
    hovertemplate="%{y} alerts<extra></extra>"
))

fig.update_layout(
    title="Traffic Volume & Anomalies (1-min intervals)",
    xaxis_title="Time", yaxis_title="Flow Count",
    hovermode="x unified", height=350,
    margin=dict(l=50, r=30, t=60, b=50),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
    font=dict(family="system-ui, -apple-system, sans-serif", size=12, color=COLORS["text"]),
    xaxis=dict(gridcolor=COLORS["grid"], zeroline=False),
    yaxis=dict(gridcolor=COLORS["grid"], zeroline=False)
)
fig.write_image(output_dir / "streamlit-timeline.png", width=800, height=350, scale=2)

# ------------------------------------------------------------------
# 2. Streamlit - Attack Breakdown
# ------------------------------------------------------------------
attacks = ["PortScan", "DoS", "Infiltration", "Botnet", "BruteForce", "WebAttack"]
counts = [1632, 922, 634, 344, 324, 161]
colors = [COLORS[a.lower()] for a in attacks]

fig = go.Figure(go.Bar(
    x=counts[::-1], y=attacks[::-1], orientation="h",
    marker=dict(color=colors[::-1], line=dict(width=0)),
    text=counts[::-1], textposition="outside",
    textfont=dict(size=11, color=COLORS["text"]),
    hovertemplate="%{y}: %{x} alerts<extra></extra>"
))
fig.update_layout(
    title="Anomalies by Attack Type",
    xaxis_title="Count", yaxis_title="",
    height=300, margin=dict(l=120, r=30, t=60, b=50),
    plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
    font=dict(family="system-ui, -apple-system, sans-serif", size=12, color=COLORS["text"]),
    xaxis=dict(gridcolor=COLORS["grid"], zeroline=False),
    yaxis=dict(gridcolor=COLORS["grid"], zeroline=False)
)
fig.write_image(output_dir / "streamlit-attack-breakdown.png", width=600, height=300, scale=2)

# ------------------------------------------------------------------
# 3. Streamlit - Protocol Distribution
# ------------------------------------------------------------------
protos = ["TCP", "UDP", "ICMP", "Other"]
proto_counts = [45200, 12800, 3200, 1800]

fig = go.Figure(go.Pie(
    labels=protos, values=proto_counts, hole=0.55,
    marker=dict(colors=[COLORS["primary"], "#34495e", "#7f8c8d", "#95a5a6"]),
    textinfo="label+percent", textfont=dict(size=12, color=COLORS["text"])
))
fig.update_layout(
    title="Protocol Distribution",
    height=300, margin=dict(l=40, r=40, t=60, b=40),
    plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
    font=dict(family="system-ui, -apple-system, sans-serif", size=12, color=COLORS["text"]),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
)
fig.write_image(output_dir / "streamlit-protocol-dist.png", width=400, height=300, scale=2)

# ------------------------------------------------------------------
# 4. Streamlit - Flow Table (as styled image)
# ------------------------------------------------------------------
# Create a table visualization
table_data = {
    "Time": ["10:45:23", "10:45:18", "10:44:55", "10:44:32", "10:44:10"],
    "Src IP": ["192.168.1.45", "192.168.1.23", "192.168.1.67", "192.168.1.12", "192.168.1.89"],
    "Src Port": [54321, 49152, 3389, 22, 8080],
    "Dst IP": ["192.168.1.10", "192.168.1.10", "192.168.1.5", "192.168.1.5", "192.168.1.20"],
    "Dst Port": [80, 80, 3389, 22, 8080],
    "Proto": ["TCP", "TCP", "TCP", "TCP", "TCP"],
    "Service": ["HTTP", "HTTP", "RDP", "SSH", "HTTP"],
    "Score": [0.947, 0.892, 0.823, 0.791, 0.756],
    "Alert": ["●", "●", "●", "●", "●"],
    "Attack": ["DoS", "PortScan", "BruteForce", "BruteForce", "WebAttack"]
}

fig = go.Figure(data=[go.Table(
    header=dict(
        values=list(table_data.keys()),
        fill_color=COLORS["primary"],
        font=dict(color="white", size=11, family="system-ui"),
        align="left", height=35
    ),
    cells=dict(
        values=list(table_data.values()),
        fill_color=[[COLORS["bg"] if i % 2 == 0 else "#f5f5fa" for i in range(5)]],
        font=dict(color=COLORS["text"], size=11, family="system-ui"),
        align="left", height=30
    )
)])
fig.update_layout(
    title="Recent Anomalous Flows",
    height=280, margin=dict(l=20, r=20, t=50, b=20),
    paper_bgcolor=COLORS["bg"]
)
fig.write_image(output_dir / "streamlit-flow-table.png", width=900, height=280, scale=2)

# ------------------------------------------------------------------
# 5. Grafana Dashboard - Overview
# ------------------------------------------------------------------
# Create a composite Grafana-style dashboard image
fig = go.Figure()

# Subplot layout: 2x3 grid
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=("Flow Volume & Anomalies", "Total Flows", "Active Anomalies",
                    "Anomalies by Attack Type", "Protocol Distribution", "Recent Flows"),
    specs=[
        [{"colspan": 2}, None, {"type": "indicator"}],
        [{"type": "bar"}, {"type": "pie"}, {"type": "table", "rowspan": 1}]
    ],
    vertical_spacing=0.12, horizontal_spacing=0.08
)

# Row 1, Col 1-2: Time series
fig.add_trace(go.Scatter(
    x=times, y=benign, name="Benign", mode="lines",
    line=dict(color=COLORS["benign"], width=2), fill="tozeroy",
    fillcolor="rgba(46, 125, 50, 0.1)", showlegend=True
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=times, y=anomalies, name="Anomalies", mode="lines",
    line=dict(color=COLORS["anomaly"], width=2), fill="tozeroy",
    fillcolor="rgba(198, 40, 40, 0.1)", showlegend=True
), row=1, col=1)

# Row 1, Col 3: Gauge - Total Flows
fig.add_trace(go.Indicator(
    mode="gauge+number", value=63000,
    gauge=dict(axis=dict(range=[None, 100000]),
               bar=dict(color=COLORS["primary"]),
               steps=[dict(range=[0, 50000], color="#e8f5e9"),
                      dict(range=[50000, 100000], color="#c8e6c9")]),
    title=dict(text="Total Flows")
), row=1, col=3)

# Row 2, Col 1: Bar chart - Anomalies by type
fig.add_trace(go.Bar(
    x=attacks, y=counts, name="Anomalies",
    marker_color=[COLORS[a.lower()] for a in attacks], showlegend=False
), row=2, col=1)

# Row 2, Col 2: Pie - Protocol
fig.add_trace(go.Pie(
    labels=protos, values=proto_counts, hole=0.5,
    marker=dict(colors=[COLORS["primary"], "#34495e", "#7f8c8d", "#95a5a6"]),
    showlegend=False, textinfo="label+percent"
), row=2, col=2)

# Row 2, Col 3: Table
fig.add_trace(go.Table(
    header=dict(values=["Time", "Src IP", "Dst IP", "Proto", "Score", "Attack"],
                fill_color=COLORS["primary"], font=dict(color="white", size=10), align="left"),
    cells=dict(values=[
        ["10:45:23", "10:45:18", "10:44:55", "10:44:32", "10:44:10"],
        ["192.168.1.45", "192.168.1.23", "192.168.1.67", "192.168.1.12", "192.168.1.89"],
        ["192.168.1.10", "192.168.1.10", "192.168.1.5", "192.168.1.5", "192.168.1.20"],
        ["TCP", "TCP", "TCP", "TCP", "TCP"],
        [0.947, 0.892, 0.823, 0.791, 0.756],
        ["DoS", "PortScan", "BruteForce", "BruteForce", "WebAttack"]
    ], fill_color=COLORS["bg"], font=dict(color=COLORS["text"], size=10), align="left")
), row=2, col=3)

fig.update_layout(
    height=700, margin=dict(l=40, r=40, t=60, b=40),
    plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
    font=dict(family="system-ui, -apple-system, sans-serif", size=11, color=COLORS["text"]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Update axes
fig.update_xaxes(gridcolor=COLORS["grid"], zeroline=False)
fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)

fig.write_image(output_dir / "grafana-dashboard.png", width=1200, height=700, scale=2)

# ------------------------------------------------------------------
# 6. Architecture Diagram
# ------------------------------------------------------------------
fig = go.Figure()

# Define boxes for architecture
boxes = [
    {"name": "PCAP<br>Files", "x": 0.5, "y": 0.9, "color": "#e8f5e9"},
    {"name": "Zeek<br>(Docker)", "x": 0.5, "y": 0.7, "color": "#e3f2fd"},
    {"name": "flows.parquet<br>Features", "x": 0.5, "y": 0.5, "color": "#fff3e0"},
    {"name": "Isolation<br>Forest Model", "x": 0.25, "y": 0.3, "color": "#fce4ec"},
    {"name": "Streamlit<br>Dashboard", "x": 0.5, "y": 0.1, "color": "#f3e5f5"},
    {"name": "Grafana<br>Dashboard", "x": 0.75, "y": 0.3, "color": "#f3e5f5"},
    {"name": "FastAPI<br>Model Server", "x": 0.75, "y": 0.1, "color": "#e8eaf6"},
]

# Arrows
arrows = [
    (0.5, 0.85, 0.5, 0.75),
    (0.5, 0.65, 0.5, 0.55),
    (0.5, 0.45, 0.3, 0.35),
    (0.3, 0.25, 0.45, 0.15),
    (0.5, 0.45, 0.65, 0.35),
    (0.65, 0.25, 0.6, 0.15),
    (0.5, 0.15, 0.6, 0.15),
]

for box in boxes:
    fig.add_shape(
        type="rect", x0=box["x"]-0.15, x1=box["x"]+0.15,
        y0=box["y"]-0.05, y1=box["y"]+0.05,
        fillcolor=box["color"], line=dict(color=COLORS["primary"], width=2),
        layer="below"
    )
    fig.add_annotation(
        x=box["x"], y=box["y"], text=box["name"],
        showarrow=False, font=dict(size=12, color=COLORS["text"], family="system-ui"),
        align="center"
    )

for x0, y0, x1, y1 in arrows:
    fig.add_annotation(
        x=x1, y=y1, ax=x0, ay=y0,
        arrowhead=2, arrowsize=1.5, arrowwidth=2,
        arrowcolor=COLORS["primary"], showarrow=True
    )

fig.update_layout(
    title="System Architecture",
    xaxis=dict(range=[0, 1], visible=False),
    yaxis=dict(range=[0, 1], visible=False),
    height=500, margin=dict(l=20, r=20, t=60, b=20),
    plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
    font=dict(family="system-ui, -apple-system, sans-serif", size=12, color=COLORS["text"])
)
fig.write_image(output_dir / "architecture.png", width=800, height=500, scale=2)

print(f"Generated images in {output_dir}")
for f in output_dir.glob("*.png"):
    print(f"  - {f.name}")