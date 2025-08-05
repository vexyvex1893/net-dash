import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Network Traffic Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .status-message {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .dismiss-btn {
        background: none;
        border: none;
        color: inherit;
        font-size: 18px;
        cursor: pointer;
        padding: 0 5px;
    }
    .dismiss-btn:hover {
        opacity: 0.7;
    }
    .dashboard-header {
        position: sticky;
        top: 0;
        background-color: #0e1117;
        z-index: 1000;
        padding: 10px 0;
        margin-bottom: 20px;
    }
    .chart-container {
        margin-top: 20px;
        padding: 0 20px;
    }
    .status-container {
        margin: 10px 0;
    }
    /* Improve chart spacing */
    .stPlotlyChart {
        margin: 10px 0;
    }
    /* Ensure charts have proper width */
    .js-plotly-plot {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for dismissible messages
if 'dismissed_messages' not in st.session_state:
    st.session_state.dismissed_messages = set()

if 'status_messages' not in st.session_state:
    st.session_state.status_messages = [
        {"id": "graylog_connection", "text": "Connected to Graylog - Found 2 system inputs", "type": "success"},
        {"id": "graylog_data", "text": "Connected to Graylog - displaying real data", "type": "success"}
    ]

def add_status_message(message_id, text, message_type="success"):
    """Add a new status message"""
    st.session_state.status_messages.append({
        "id": message_id,
        "text": text,
        "type": message_type
    })

def dismiss_message(message_id):
    """Dismiss a status message"""
    st.session_state.dismissed_messages.add(message_id)

def display_status_messages():
    """Display status messages with dismiss buttons using Streamlit components"""
    active_messages = [msg for msg in st.session_state.status_messages 
                      if msg["id"] not in st.session_state.dismissed_messages]
    
    if active_messages:
        st.markdown('<div class="status-container">', unsafe_allow_html=True)
        
        for message in active_messages:
            col1, col2 = st.columns([20, 1])
            
            with col1:
                if message["type"] == "success":
                    st.success(message["text"])
                else:
                    st.error(message["text"])
            
            with col2:
                if st.button("×", key=f"dismiss_{message['id']}", help="Dismiss message"):
                    dismiss_message(message["id"])
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_sample_data():
    """Create sample data for the dashboard"""
    # Traffic source distribution
    traffic_sources = {
        'Web Server': 51.3,
        'Router': 29.9,
        'Email Server': 12.9,
        'IoT Devices': 5.85
    }
    
    # Traffic over time
    times = pd.date_range(start='2025-08-05 06:00', end='2025-08-05 18:00', freq='H')
    total_traffic = np.random.randint(8000, 14000, len(times))
    blocked_traffic = np.random.randint(0, 200, len(times))
    allowed_traffic = total_traffic - blocked_traffic
    
    # Traffic type distribution
    traffic_types = {
        'HTTP/HTTPS': 3800,
        'DNS': 1600,
        'SMTP': 2000,
        'SSH': 600,
        'Other': 400
    }
    
    # Security events
    security_events = [
        {'timestamp': '2025-08-05 23:35:47', 'type': 'Unauthorized Access', 'severity': 'Low', 'source': '192.168.1.234', 'status': 'Allowed'},
        {'timestamp': '2025-08-05 23:34:47', 'type': 'Port Scan', 'severity': 'Medium', 'source': '192.168.1.56', 'status': 'Blocked'}
    ]
    
    # System events
    system_events = [
        {'timestamp': '2025-08-05 23:35:47', 'type': 'Resource Alert', 'category': 'System', 'description': 'System event 1 occurred', 'status': 'Completed'},
        {'timestamp': '2025-08-05 23:34:47', 'type': 'Service Restart', 'category': 'System', 'description': 'System event 2 occurred', 'status': 'Failed'}
    ]
    
    return traffic_sources, times, total_traffic, blocked_traffic, allowed_traffic, traffic_types, security_events, system_events

def create_traffic_source_chart(traffic_sources):
    """Create donut chart for traffic source distribution"""
    fig = go.Figure(data=[go.Pie(
        labels=list(traffic_sources.keys()),
        values=list(traffic_sources.values()),
        hole=0.4,
        marker_colors=['#90EE90', '#FF6B6B', '#87CEEB', '#20B2AA']
    )])
    
    fig.update_layout(
        title="Traffic Source Distribution",
        showlegend=True,
        height=450,
        width=400,
        margin=dict(l=10, r=10, t=50, b=10),
        title_x=0.5,
        title_font_size=16
    )
    return fig

def create_traffic_over_time_chart(times, total_traffic, blocked_traffic, allowed_traffic):
    """Create line chart for traffic over time"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=total_traffic,
        mode='lines',
        name='Total Traffic',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=times,
        y=blocked_traffic,
        mode='lines',
        name='Blocked Traffic',
        line=dict(color='red', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=times,
        y=allowed_traffic,
        mode='lines',
        name='Allowed Traffic',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title="Traffic Over Time",
        xaxis_title="Time",
        yaxis_title="Value",
        height=450,
        width=400,
        margin=dict(l=10, r=10, t=50, b=10),
        title_x=0.5,
        title_font_size=16,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def create_traffic_type_chart(traffic_types):
    """Create bar chart for traffic type distribution"""
    fig = go.Figure(data=[go.Bar(
        x=list(traffic_types.keys()),
        y=list(traffic_types.values()),
        marker_color=['#20B2AA', '#FFD700', '#9370DB', '#FF6B6B', '#87CEEB']
    )])
    
    fig.update_layout(
        title="Traffic Type Distribution",
        xaxis_title="Traffic Type",
        yaxis_title="Value",
        height=450,
        width=400,
        margin=dict(l=10, r=10, t=50, b=10),
        title_x=0.5,
        title_font_size=16
    )
    return fig

def main():
    # Dashboard header with proper spacing - always visible
    st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
    
    # Title and dropdown in a row with proper spacing
    col1, col2, col3 = st.columns([4, 2, 1])
    
    with col1:
        st.title("Network Traffic Dashboard")
    
    with col2:
        st.write("")  # Add some spacing
        time_period = st.selectbox(
            "Time Period",
            ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
            key="time_period"
        )
    
    with col3:
        st.write("")  # Empty space for alignment
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display status messages with dismiss functionality
    display_status_messages()
    
    # Create sample data
    traffic_sources, times, total_traffic, blocked_traffic, allowed_traffic, traffic_types, security_events, system_events = create_sample_data()
    
    # Charts section with improved spacing
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Create three columns for charts with better spacing
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        fig1 = create_traffic_source_chart(traffic_sources)
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        fig2 = create_traffic_over_time_chart(times, total_traffic, blocked_traffic, allowed_traffic)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    
    with col3:
        fig3 = create_traffic_type_chart(traffic_types)
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tables section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Security Events")
        security_df = pd.DataFrame(security_events)
        st.dataframe(security_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("System Events")
        system_df = pd.DataFrame(system_events)
        st.dataframe(system_df, use_container_width=True, hide_index=True)
    
    # Add a button to manually dismiss all messages (for testing)
    if st.button("Dismiss All Messages"):
        st.session_state.dismissed_messages.update([msg["id"] for msg in st.session_state.status_messages])
        st.rerun()
    
    # Add a button to add a test message (for testing)
    if st.button("Add Test Message"):
        add_status_message("test_message", "This is a test message", "success")
        st.rerun()

if __name__ == "__main__":
    main() 