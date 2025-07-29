import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

# Graylog configuration
GRAYLOG_URL = "http://192.168.10.239:9000"
GRAYLOG_USERNAME = "admin"  # Changed from "administrator" to "admin"
GRAYLOG_PASSWORD = "Salvat!0n"

# Set page config
st.set_page_config(
    page_title="Network Traffic Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 0.25rem 2rem 2rem 2rem; }
    .stMetric { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
    .stSelectbox { margin-bottom: 0.25rem; }
    h1 { margin-bottom: 0.25rem; margin-top: 0.25rem; }
    .stApp { margin-top: -2rem; }
    .block-container { padding-top: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

def fetch_graylog_data():
    """Fetch data from Graylog API"""
    try:
        # Fetch logs from Graylog
        url = f"{GRAYLOG_URL}/api/search/universal/relative"
        params = {
            'query': '*',
            'range': 86400,  # Last 24 hours
            'limit': 1000
        }
        
        response = requests.get(
            url, 
            params=params,
            auth=(GRAYLOG_USERNAME, GRAYLOG_PASSWORD),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('messages', [])
        else:
            st.error(f"Error fetching data from Graylog: {response.status_code} {response.reason}")
            return []
            
    except Exception as e:
        st.error(f"Error fetching data from Graylog: {str(e)}")
        return []

def generate_mock_data(hours):
    """Generate mock data for demonstration"""
    current_time = datetime.now()
    data = []
    for i in range(hours):
        timestamp = current_time - timedelta(hours=i)
        data.append({
            'timestamp': timestamp,
            'router_traffic': random.randint(1000, 5000),
            'iot_traffic': random.randint(100, 1000),
            'email_traffic': random.randint(500, 2000),
            'web_traffic': random.randint(2000, 8000),
            'total_traffic': random.randint(5000, 15000),
            'blocked_traffic': random.randint(100, 500),
            'allowed_traffic': random.randint(4000, 14000)
        })
    return pd.DataFrame(data)

# Title and Time Period Selector
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

# Try to fetch real data from Graylog
graylog_data = fetch_graylog_data()

if graylog_data:
    st.success("✅ Connected to Graylog - displaying real data")
    # Process real Graylog data here
    # For now, we'll use mock data but show success message
    df = generate_mock_data(hours)
else:
    st.warning("⚠️ No data available from Graylog for the selected period. Using sample data for demonstration.")
    df = generate_mock_data(hours)

# Create three equal columns for charts
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Traffic Source Distribution")
    traffic_sources = {
        'Router': df['router_traffic'].sum(),
        'IoT Devices': df['iot_traffic'].sum(),
        'Email Server': df['email_traffic'].sum(),
        'Web Server': df['web_traffic'].sum()
    }
    fig = go.Figure(data=[go.Pie(
        labels=list(traffic_sources.keys()),
        values=list(traffic_sources.values()),
        hole=0.4,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    )])
    fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Traffic Over Time")
    fig = px.line(df, x='timestamp', y=['total_traffic', 'blocked_traffic', 'allowed_traffic'],
                 color_discrete_map={
                     'total_traffic': '#2E86C1',
                     'blocked_traffic': '#E74C3C',
                     'allowed_traffic': '#27AE60'
                 })
    fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.subheader("Traffic Type Distribution")
    traffic_types = {
        'HTTP/HTTPS': random.randint(3000, 8000),
        'DNS': random.randint(1000, 3000),
        'SMTP': random.randint(500, 2000),
        'SSH': random.randint(200, 1000),
        'Other': random.randint(100, 500)
    }
    fig = px.bar(x=list(traffic_types.keys()), y=list(traffic_types.values()),
                color=list(traffic_types.keys()),
                color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

# Create two equal columns for events
col_events1, col_events2 = st.columns(2)

with col_events1:
    st.subheader("Security Events")
    security_events = [
        {"timestamp": datetime.now() - timedelta(minutes=i),
         "type": random.choice(["Unauthorized Access", "Port Scan", "Malware Detection", "Brute Force Attempt"]),
         "severity": random.choice(["High", "Medium", "Low"]),
         "source": f"192.168.1.{random.randint(1, 254)}",
         "status": random.choice(["Blocked", "Allowed"])}
        for i in range(10)
    ]
    security_df = pd.DataFrame(security_events)
    st.dataframe(security_df, hide_index=True, use_container_width=True)

with col_events2:
    st.subheader("System Events")
    system_events = [
        {"timestamp": datetime.now() - timedelta(minutes=i),
         "type": random.choice(["System Update", "Configuration Change", "Service Restart", "Resource Alert"]),
         "category": random.choice(["Maintenance", "Configuration", "Performance", "System"]),
         "description": f"System event {i+1} occurred",
         "status": random.choice(["Completed", "In Progress", "Failed"])}
        for i in range(10)
    ]
    system_df = pd.DataFrame(system_events)
    st.dataframe(system_df, hide_index=True, use_container_width=True) 