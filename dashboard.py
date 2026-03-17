import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

st.set_page_config(layout="wide", page_title="SecurityDouble SOC")

st.title("🛡️ SecurityDouble AI WAF SOC Dashboard")

LOG_FILE = "attack_logs.csv"


if not os.path.exists(LOG_FILE):
    st.error("No attack logs found. Run ai_waf.py first.")
    st.stop()

# Load logs with fixed column structure
df = pd.read_csv(
    LOG_FILE,
    names=[
        "timestamp",
        "ip",
        "payload",
        "attack_type",
        "action",
        "score",
        "severity",
        "lat",
        "lon"
    ],
    header=0
)

# Fix timestamp parsing
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Extract ID from payload
def extract_id(payload):

    match = re.search(r"id=([0-9]+)", str(payload))

    if match:
        return match.group(1)

    return ""

df["id"] = df["payload"].apply(extract_id)

# ======================
# METRICS
# ======================

col1,col2,col3,col4 = st.columns(4)

col1.metric("Total Requests",len(df))
col2.metric("Blocked Attacks",len(df[df["action"]=="BLOCKED"]))
col3.metric("Allowed Traffic",len(df[df["action"]=="ALLOWED"]))
col4.metric("Threat Score",int(df["score"].sum()))

# ======================
# PIE + BAR
# ======================

left,right = st.columns(2)

with left:

    st.subheader("Attack Distribution")

    pie = px.pie(df,names="attack_type")

    st.plotly_chart(pie,use_container_width=True)

with right:

    st.subheader("Attack Frequency")

    counts = df["attack_type"].value_counts().reset_index()

    counts.columns=["attack_type","count"]

    bar = px.bar(counts,x="attack_type",y="count")

    st.plotly_chart(bar,use_container_width=True)

# ======================
# TIMELINE
# ======================

st.subheader("SOC Timeline")

df_sorted = df.sort_values("timestamp")

df_sorted["request_count"] = range(1,len(df_sorted)+1)

timeline = px.line(
df_sorted,
x="timestamp",
y="request_count"
)

st.plotly_chart(timeline,use_container_width=True)
st.subheader("🚨 Real-Time SOC Alerts")

recent = df.tail(1)

if not recent.empty:
    attack = recent["attack_type"].values[0]
    ip = recent["ip"].values[0]

    if attack != "Normal":
        st.error(f"⚠️ {attack} attack detected from IP: {ip}")
    else:
        st.success("✅ No active threats detected")
# ======================
# ATTACK MAP
# ======================

st.subheader("Global Attack Map")

if "lat" in df.columns and "lon" in df.columns:

    st.map(df[["lat","lon"]])

# ======================
# TOP ATTACKERS
# ======================

st.subheader("Top Attacking IPs")

attackers = df[df["action"]=="BLOCKED"]

if not attackers.empty:

    top_ips = attackers["ip"].value_counts().reset_index()

    top_ips.columns=["ip","attack_count"]

    st.dataframe(top_ips.head(10))

else:

    st.write("No attacks detected yet")

# ======================
# ALERT
# ======================

recent = df.tail(1)

if not recent.empty and recent["attack_type"].values[0]!="Normal":

    st.warning(
    f"🚨 {recent['attack_type'].values[0]} attack detected from {recent['ip'].values[0]}"
    )

# ======================
# LIVE LOGS
# ======================

st.subheader("Live Logs (Last 50 Requests)")

st.dataframe(
df[
[
"timestamp",
"ip",
"id",
"payload",
"attack_type",
"action",
"score",
"severity"
]
].tail(50)
)