import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import requests

# --- Graylog API Configuration ---
GRAYLOG_API_URL = "http://192.168.10.239:9000/api/search/universal/relative"
GRAYLOG_USERNAME = "administrator"
GRAYLOG_PASSWORD = "Salvat!0n"

# --- Helper function to fetch data from Graylog ---
def fetch_graylog_data(hours=24, query="*"):
    params = {
        "query": query,
        "range": hours * 3600,  # seconds
        "limit": 1000  # adjust as needed
    }
    try:
        response = requests.get(
            GRAYLOG_API_URL,
            params=params,
            auth=(GRAYLOG_USERNAME, GRAYLOG_PASSWORD),  # Use HTTP Basic Auth
            headers={"Accept": "application/json"},
            verify=False
        )
        response.raise_for_status()
        data = response.json()
        messages = data.get("messages", [])
        # Flatten messages
        records = [msg["message"] for msg in messages]
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Error fetching data from Graylog: {e}")
        return pd.DataFrame([])

# --- Streamlit UI ---
st.set_page_config(
    page_title="Network Traffic Dashboard",
    page_icon="🌐",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        padding: 0.5rem 2rem 2rem 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stSelectbox {
        margin-bottom: 0.5rem;
    }
    h1 {
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

col_title, col_selector = st.columns([3, 1])
with col_title:
    st.title("🌐 Network Traffic Dashboard")
with col_selector:
    time_period = st.selectbox(
        "Display Period",
        options=["Last 1 hour", "Last 6 hours", "Last 12 hours", "Last 24 hours", "Last 7 days"],
        index=3
    )

time_period_map = {
    "Last 1 hour": 1,
    "Last 6 hours": 6,
    "Last 12 hours": 12,
    "Last 24 hours": 24,
    "Last 7 days": 168
}
hours = time_period_map[time_period]

# --- Fetch data from Graylog ---
df = fetch_graylog_data(hours=hours)

if df.empty:
    st.warning("No data available from Graylog for the selected period.")
    st.stop()

# --- Example field mapping (adjust as needed to match your Graylog message fields) ---
# You may need to update these field names to match your Graylog setup
router_traffic = df.get('router_traffic', pd.Series([0]*len(df)))
iot_traffic = df.get('iot_traffic', pd.Series([0]*len(df)))
email_traffic = df.get('email_traffic', pd.Series([0]*len(df)))
web_traffic = df.get('web_traffic', pd.Series([0]*len(df)))
total_traffic = df.get('total_traffic', pd.Series([0]*len(df)))
blocked_traffic = df.get('blocked_traffic', pd.Series([0]*len(df)))
allowed_traffic = df.get('allowed_traffic', pd.Series([0]*len(df)))

# --- Main Charts ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Traffic Source Distribution")
    traffic_sources = {
        'Router': router_traffic.sum(),
        'IoT Devices': iot_traffic.sum(),
        'Email Server': email_traffic.sum(),
        'Web Server': web_traffic.sum()
    }
    fig = go.Figure(data=[go.Pie(
        labels=list(traffic_sources.keys()),
        values=list(traffic_sources.values()),
        hole=0.4,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Traffic Volume: %{value:,.0f} bytes<br>Percentage: %{percent}<extra></extra>"
    )])
    fig.update_layout(showlegend=True, height=400, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Traffic Over Time")
    if 'timestamp' in df.columns:
        fig = px.line(df, x='timestamp', y=['total_traffic', 'blocked_traffic', 'allowed_traffic'],
                     title=f'Network Traffic Over Time ({time_period})',
                     labels={'value': 'Traffic Volume (bytes)', 'timestamp': 'Time'},
                     color_discrete_map={
                         'total_traffic': '#2E86C1',
                         'blocked_traffic': '#E74C3C',
                         'allowed_traffic': '#27AE60'
                     })
        fig.update_layout(showlegend=True, height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timestamp data available for time series chart.")

with col3:
    st.subheader("Traffic Type Distribution")
    # Example: You may need to aggregate by protocol if available in your Graylog data
    if 'protocol' in df.columns and 'traffic_volume' in df.columns:
        protocol_df = df.groupby('protocol')['traffic_volume'].sum().reset_index()
        fig = px.bar(protocol_df, x='protocol', y='traffic_volume',
                    title=f'Traffic by Protocol ({time_period})',
                    labels={'protocol': 'Protocol', 'traffic_volume': 'Traffic Volume (bytes)'},
                    color='protocol',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(showlegend=False, height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No protocol data available for protocol distribution chart.")

# --- Events Tables ---
col_events1, col_events2 = st.columns(2)

with col_events1:
    st.subheader("Security Events")
    # Example: Filter for security events if you have a field like 'event_type' or 'security_event'
    if 'event_type' in df.columns:
        security_df = df[df['event_type'].str.contains('security', case=False, na=False)]
        st.dataframe(
            security_df,
            column_config={
                "timestamp": "Time",
                "type": "Event Type",
                "severity": "Severity",
                "source": "Source IP",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No security event data available.")

with col_events2:
    st.subheader("System Events")
    # Example: Filter for system events if you have a field like 'event_type' or 'system_event'
    if 'event_type' in df.columns:
        system_df = df[df['event_type'].str.contains('system', case=False, na=False)]
        st.dataframe(
            system_df,
            column_config={
                "timestamp": "Time",
                "type": "Event Type",
                "category": "Category",
                "description": "Description",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No system event data available.")

# --- End of file ---

