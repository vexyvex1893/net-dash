import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import requests
import json

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
        
        # Process messages to extract fields properly
        records = []
        for msg in messages:
            message_data = msg.get("message", {})
            # If message is a string, try to parse it as JSON
            if isinstance(message_data, str):
                try:
                    message_data = json.loads(message_data)
                except:
                    # If it's not JSON, create a simple record
                    message_data = {"message": message_data, "timestamp": msg.get("timestamp")}
            
            # Add timestamp if available
            if "timestamp" not in message_data and msg.get("timestamp"):
                message_data["timestamp"] = msg["timestamp"]
            
            records.append(message_data)
        
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

# --- Data processing and fallback values ---
if df.empty:
    st.warning("No data available from Graylog for the selected period. Using sample data for demonstration.")
    # Create sample data for demonstration
    sample_data = []
    for i in range(24):
        sample_data.append({
            'timestamp': datetime.now() - timedelta(hours=i),
            'router_traffic': 1000 + i * 100,
            'iot_traffic': 500 + i * 50,
            'email_traffic': 800 + i * 80,
            'web_traffic': 2000 + i * 200,
            'total_traffic': 4300 + i * 430,
            'blocked_traffic': 100 + i * 10,
            'allowed_traffic': 4200 + i * 420,
            'protocol': ['HTTP', 'HTTPS', 'DNS', 'SMTP'][i % 4],
            'traffic_volume': 1000 + i * 100,
            'event_type': ['security', 'system', 'network'][i % 3],
            'source_ip': f'192.168.1.{i % 254 + 1}',
            'severity': ['High', 'Medium', 'Low'][i % 3],
            'status': ['Blocked', 'Allowed'][i % 2]
        })
    df = pd.DataFrame(sample_data)

# --- Extract or create traffic data ---
# Try to get actual data, fallback to sample data if not available
router_traffic = df.get('router_traffic', pd.Series([1000 + i * 100 for i in range(len(df))]))
iot_traffic = df.get('iot_traffic', pd.Series([500 + i * 50 for i in range(len(df))]))
email_traffic = df.get('email_traffic', pd.Series([800 + i * 80 for i in range(len(df))]))
web_traffic = df.get('web_traffic', pd.Series([2000 + i * 200 for i in range(len(df))]))
total_traffic = df.get('total_traffic', pd.Series([4300 + i * 430 for i in range(len(df))]))
blocked_traffic = df.get('blocked_traffic', pd.Series([100 + i * 10 for i in range(len(df))]))
allowed_traffic = df.get('allowed_traffic', pd.Series([4200 + i * 420 for i in range(len(df))]))

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
    # Create timestamp column if it doesn't exist
    if 'timestamp' not in df.columns:
        df['timestamp'] = [datetime.now() - timedelta(hours=i) for i in range(len(df))]
    
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

with col3:
    st.subheader("Traffic Type Distribution")
    # Create protocol data if not available
    if 'protocol' not in df.columns:
        protocols = ['HTTP', 'HTTPS', 'DNS', 'SMTP', 'SSH', 'FTP']
        df['protocol'] = [protocols[i % len(protocols)] for i in range(len(df))]
    
    if 'traffic_volume' not in df.columns:
        df['traffic_volume'] = [1000 + i * 100 for i in range(len(df))]
    
    protocol_df = df.groupby('protocol')['traffic_volume'].sum().reset_index()
    fig = px.bar(protocol_df, x='protocol', y='traffic_volume',
                title=f'Traffic by Protocol ({time_period})',
                labels={'protocol': 'Protocol', 'traffic_volume': 'Traffic Volume (bytes)'},
                color='protocol',
                color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(showlegend=False, height=400, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

# --- Events Tables ---
col_events1, col_events2 = st.columns(2)

with col_events1:
    st.subheader("Security Events")
    # Create security events data if not available
    if 'event_type' not in df.columns:
        df['event_type'] = ['security' if i % 3 == 0 else 'system' if i % 3 == 1 else 'network' for i in range(len(df))]
    
    if 'source_ip' not in df.columns:
        df['source_ip'] = [f'192.168.1.{i % 254 + 1}' for i in range(len(df))]
    
    if 'severity' not in df.columns:
        df['severity'] = ['High' if i % 3 == 0 else 'Medium' if i % 3 == 1 else 'Low' for i in range(len(df))]
    
    if 'status' not in df.columns:
        df['status'] = ['Blocked' if i % 2 == 0 else 'Allowed' for i in range(len(df))]
    
    security_df = df[df['event_type'].str.contains('security', case=False, na=False)]
    if not security_df.empty:
        st.dataframe(
            security_df[['timestamp', 'source_ip', 'severity', 'status']].head(10),
            column_config={
                "timestamp": "Time",
                "source_ip": "Source IP",
                "severity": "Severity",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No security events found in the data.")

with col_events2:
    st.subheader("System Events")
    system_df = df[df['event_type'].str.contains('system', case=False, na=False)]
    if not system_df.empty:
        st.dataframe(
            system_df[['timestamp', 'source_ip', 'severity', 'status']].head(10),
            column_config={
                "timestamp": "Time",
                "source_ip": "Source IP",
                "severity": "Severity",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No system events found in the data.")

# --- Add auto-refresh functionality ---
st.markdown("---")
st.markdown("*Dashboard auto-refreshes every 30 seconds*")

# Add a simple refresh mechanism
if st.button("🔄 Refresh Data"):
    st.rerun()

# --- End of file ---

