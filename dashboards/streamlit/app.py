import yaml
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta

with open("config.yaml") as f:
    config = yaml.safe_load(f)

data_dir = Path(config["paths"]["data_dir"])
predictions_file = data_dir / "predictions.parquet"
flows_file = data_dir / "flows.parquet"

st.set_page_config(
    page_title="Network Anomaly Detection",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

ATTACK_COLORS = config["dashboard"]["attack_colors"]
MITRE_TECHNIQUES = config["mitre_attack"]["techniques"]

@st.cache_data(ttl=30)
def load_data():
    if not predictions_file.exists():
        return pd.DataFrame(), pd.DataFrame()
    preds = pd.read_parquet(predictions_file)
    flows = pd.read_parquet(flows_file) if flows_file.exists() else pd.DataFrame()
    return preds, flows

def render_header():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("Network Anomaly Detection")
        st.caption("Real-time flow analysis · Isolation Forest · MITRE ATT&CK mapping")
    with col2:
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
        if auto_refresh:
            st.rerun()

def render_metrics(preds: pd.DataFrame):
    total = len(preds)
    anomalies = int(preds["is_anomaly"].sum()) if "is_anomaly" in preds.columns else 0
    benign = total - anomalies
    anomaly_rate = (anomalies / total * 100) if total > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Flows", f"{total:,}")
    m2.metric("Anomalies", f"{anomalies:,}", delta=f"{anomaly_rate:.2f}%")
    m3.metric("Benign", f"{benign:,}")
    m4.metric("Unique Attacks", f"{preds['predicted_attack'].nunique() if 'predicted_attack' in preds.columns else 0}")

def render_timeline(preds: pd.DataFrame):
    if "ts" not in preds.columns or preds.empty:
        return

    df = preds.copy()
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.set_index("ts").resample("1min").agg({
        "is_anomaly": "sum",
        "uid": "count"
    }).reset_index()
    df.columns = ["timestamp", "anomalies", "total_flows"]
    df["benign"] = df["total_flows"] - df["anomalies"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["benign"],
        name="Benign", mode="lines",
        line=dict(color="#2e7d32", width=2),
        fill="tozeroy", fillcolor="rgba(46, 125, 50, 0.1)"
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["anomalies"],
        name="Anomalies", mode="lines",
        line=dict(color="#c62828", width=2),
        fill="tozeroy", fillcolor="rgba(198, 40, 40, 0.1)"
    ))
    fig.update_layout(
        title="Traffic Volume & Anomalies (1-min intervals)",
        xaxis_title="Time", yaxis_title="Flow Count",
        hovermode="x unified", height=350,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#1a1a2e"),
        xaxis=dict(gridcolor="#e8e8e8", zeroline=False),
        yaxis=dict(gridcolor="#e8e8e8", zeroline=False)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_attack_breakdown(preds: pd.DataFrame):
    if "predicted_attack" not in preds.columns or preds.empty:
        return

    attack_counts = preds[preds["is_anomaly"] == 1]["predicted_attack"].value_counts()
    if attack_counts.empty:
        st.info("No anomalies detected in current window")
        return

    fig = go.Figure(go.Bar(
        x=attack_counts.values[::-1],
        y=attack_counts.index[::-1],
        orientation="h",
        marker=dict(
            color=[ATTACK_COLORS.get(a, "#666") for a in attack_counts.index[::-1]],
            line=dict(width=0)
        ),
        text=attack_counts.values[::-1],
        textposition="outside",
        textfont=dict(size=11, color="#1a1a2e")
    ))
    fig.update_layout(
        title="Anomalies by Attack Type",
        xaxis_title="Count", yaxis_title="",
        height=300, margin=dict(l=120, r=40, t=50, b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#1a1a2e"),
        xaxis=dict(gridcolor="#e8e8e8", zeroline=False),
        yaxis=dict(gridcolor="#e8e8e8", zeroline=False)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_mitre_mapping():
    st.subheader("MITRE ATT&CK Technique Mapping")
    cols = st.columns(3)
    for idx, (tech_id, tech_name) in enumerate(MITRE_TECHNIQUES.items()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                border-left: 4px solid #2c3e50;
                padding: 12px 16px;
                margin-bottom: 8px;
                border-radius: 0 4px 4px 0;
            ">
                <code style="font-size: 13px; color: #2c3e50; font-weight: 600;">{tech_id}</code>
                <div style="font-size: 13px; color: #333; margin-top: 4px;">{tech_name}</div>
            </div>
            """, unsafe_allow_html=True)

def render_flow_table(preds: pd.DataFrame):
    if preds.empty:
        return

    display_cols = ["ts", "id_orig_h", "id_orig_p", "id_resp_h", "id_resp_p",
                    "proto", "service", "anomaly_score", "is_anomaly", "predicted_attack"]
    available = [c for c in display_cols if c in preds.columns]
    df = preds[available].copy()
    df["ts"] = pd.to_datetime(df["ts"]).dt.strftime("%H:%M:%S")

    def style_row(row):
        if row["is_anomaly"] == 1:
            attack = row.get("predicted_attack", "Unknown")
            color = ATTACK_COLORS.get(attack, "#c62828")
            return [f"background-color: {color}15; color: {color}"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df.sort_values("ts", ascending=False).head(config["dashboard"]["max_alerts"]),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ts": "Time",
            "id_orig_h": "Src IP",
            "id_orig_p": "Src Port",
            "id_resp_h": "Dst IP",
            "id_resp_p": "Dst Port",
            "proto": "Proto",
            "service": "Service",
            "anomaly_score": st.column_config.NumberColumn("Score", format="%.3f"),
            "is_anomaly": st.column_config.CheckboxColumn("Alert"),
            "predicted_attack": "Attack Type"
        }
    )

def render_protocol_distribution(preds: pd.DataFrame):
    if "proto" not in preds.columns or preds.empty:
        return

    proto_counts = preds["proto"].value_counts()
    fig = go.Figure(go.Pie(
        labels=proto_counts.index,
        values=proto_counts.values,
        hole=0.55,
        marker=dict(colors=["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#bdc3c7"]),
        textinfo="label+percent",
        textfont=dict(size=12, color="#1a1a2e")
    ))
    fig.update_layout(
        title="Protocol Distribution",
        height=300, margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#1a1a2e"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    preds, flows = load_data()

    render_header()

    if preds.empty:
        st.warning("No prediction data available. Run `make train` and `make predict` first.")
        return

    render_metrics(preds)

    tab1, tab2, tab3, tab4 = st.tabs(["Timeline", "Attack Breakdown", "Flow Details", "MITRE ATT&CK"])

    with tab1:
        c1, c2 = st.columns([2, 1])
        with c1:
            render_timeline(preds)
        with c2:
            render_protocol_distribution(preds)

    with tab2:
        render_attack_breakdown(preds)

    with tab3:
        render_flow_table(preds)

    with tab4:
        render_mitre_mapping()

    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · Data source: {predictions_file.name}")

if __name__ == "__main__":
    main()