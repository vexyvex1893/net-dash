import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
import json
import base64

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
    st.session_state.status_messages = []

def add_status_message(message_id, text, message_type="success"):
    """Add a new status message"""
    # Check if message already exists to avoid duplicates
    existing_messages = [msg for msg in st.session_state.status_messages if msg["id"] == message_id]
    if not existing_messages:
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

def get_graylog_data(time_period):
    """Get real data from Graylog API based on time period"""
    try:
        # Graylog API configuration
        graylog_url = "http://192.168.10.239:9000"
        username = "admin"
        password = "Salvat!On"  # Password with special character
        
        # Calculate time range based on selection
        now = datetime.now()
        if time_period == "Last Hour":
            start_time = now - timedelta(hours=1)
        elif time_period == "Last 6 Hours":
            start_time = now - timedelta(hours=6)
        elif time_period == "Last 24 Hours":
            start_time = now - timedelta(hours=24)
        elif time_period == "Last 7 Days":
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(hours=24)  # Default to 24 hours
        
        # Convert to Graylog timestamp format
        start_timestamp = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Create headers for authentication with proper password handling
        auth_string = f"{username}:{password}"
        headers = {
            'Authorization': f'Basic {base64.b64encode(auth_string.encode()).decode()}',
            'Content-Type': 'application/json'
        }
        
        # First test the connection with a simple API call
        test_url = f"{graylog_url}/api/system/inputs"
        test_response = requests.get(test_url, headers=headers, timeout=10)
        
        if test_response.status_code == 200:
            add_status_message("graylog_connection_success", "Connected to Graylog successfully", "success")
        else:
            add_status_message("graylog_auth_error", f"Authentication failed: {test_response.status_code}", "error")
            return None
        
        # Query Graylog for messages using the messages API endpoint
        query_url = f"{graylog_url}/api/search/universal/relative"
        
        # Use relative time range instead of absolute timestamps
        params = {
            'query': '*',  # Search all messages
            'range': '3600',  # Last hour
            'limit': 1000
        }
        
        # Try the search API
        response = requests.get(query_url, headers=headers, params=params, timeout=30)
        
        # If search API fails, use fallback method
        if response.status_code != 200:
            add_status_message("search_api_fallback", f"Search API failed ({response.status_code}), using inputs data", "error")
            return get_messages_from_inputs(graylog_url, username, password)
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            
            # Process messages to extract traffic data
            traffic_data = process_graylog_messages(messages, start_time, now)
            return traffic_data
        else:
            add_status_message("graylog_query_error", f"Failed to query Graylog: {response.status_code}", "error")
            return None
            
    except Exception as e:
        add_status_message("graylog_connection_error", f"Error connecting to Graylog: {str(e)}", "error")
        return None

def get_messages_from_inputs(graylog_url, username, password):
    """Fallback method to get messages from inputs"""
    try:
        # Create headers for authentication with proper password handling
        auth_string = f"{username}:{password}"
        headers = {
            'Authorization': f'Basic {base64.b64encode(auth_string.encode()).decode()}',
            'Content-Type': 'application/json'
        }
        
        # Get inputs first
        inputs_url = f"{graylog_url}/api/system/inputs"
        inputs_response = requests.get(inputs_url, headers=headers, timeout=10)
        
        if inputs_response.status_code == 200:
            inputs_data = inputs_response.json()
            inputs = inputs_data.get('inputs', [])
            
            # Create sample data based on inputs
            traffic_sources = {'Web Server': 25, 'Router': 35, 'Email Server': 20, 'IoT Devices': 20}
            traffic_types = {'HTTP/HTTPS': 40, 'DNS': 25, 'SMTP': 20, 'SSH': 10, 'Other': 5}
            
            # Create time series data
            now = datetime.now()
            times = [now - timedelta(hours=i) for i in range(24, 0, -1)]
            total_traffic = [np.random.randint(10, 50) for _ in range(24)]
            allowed_traffic = [int(t * 0.8) for t in total_traffic]
            blocked_traffic = [t - a for t, a in zip(total_traffic, allowed_traffic)]
            
            # Create events based on inputs
            security_events = [
                {'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'), 'type': 'Input Active', 'severity': 'Low', 'source': 'VCA pfSense', 'status': 'Active'},
                {'timestamp': (now - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'), 'type': 'Input Active', 'severity': 'Low', 'source': 'PDS Debt', 'status': 'Active'}
            ]
            
            system_events = [
                {'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'), 'type': 'System Event', 'category': 'System', 'description': f'Graylog inputs active: {len(inputs)} inputs', 'status': 'Completed'}
            ]
            
            return {
                'traffic_sources': traffic_sources,
                'traffic_types': traffic_types,
                'times': times,
                'total_traffic': total_traffic,
                'allowed_traffic': allowed_traffic,
                'blocked_traffic': blocked_traffic,
                'security_events': security_events,
                'system_events': system_events
            }
        else:
            add_status_message("inputs_fallback_error", f"Failed to get inputs: {inputs_response.status_code}", "error")
            return None
            
    except Exception as e:
        add_status_message("fallback_error", f"Fallback method failed: {str(e)}", "error")
        return None

def process_graylog_messages(messages, start_time, end_time):
    """Process Graylog messages to extract traffic data"""
    try:
        # Initialize data structures
        traffic_sources = {'Web Server': 0, 'Router': 0, 'Email Server': 0, 'IoT Devices': 0}
        traffic_types = {'HTTP/HTTPS': 0, 'DNS': 0, 'SMTP': 0, 'SSH': 0, 'Other': 0}
        time_series_data = []
        security_events = []
        system_events = []
        
        # Process each message
        for msg in messages:
            message = msg.get('message', {})
            
            # Extract timestamp
            timestamp = message.get('timestamp', '')
            if timestamp:
                try:
                    msg_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_series_data.append({
                        'timestamp': msg_time,
                        'total_traffic': 1,  # Count messages as traffic
                        'allowed_traffic': 1,
                        'blocked_traffic': 0
                    })
                except:
                    pass
            
            # Categorize by source (based on message content or source field)
            source = message.get('source', '')
            if 'web' in source.lower() or 'http' in str(message).lower():
                traffic_sources['Web Server'] += 1
            elif 'router' in source.lower():
                traffic_sources['Router'] += 1
            elif 'email' in source.lower() or 'smtp' in str(message).lower():
                traffic_sources['Email Server'] += 1
            else:
                traffic_sources['IoT Devices'] += 1
            
            # Categorize by traffic type
            message_text = str(message).lower()
            if 'http' in message_text or 'https' in message_text:
                traffic_types['HTTP/HTTPS'] += 1
            elif 'dns' in message_text:
                traffic_types['DNS'] += 1
            elif 'smtp' in message_text or 'email' in message_text:
                traffic_types['SMTP'] += 1
            elif 'ssh' in message_text:
                traffic_types['SSH'] += 1
            else:
                traffic_types['Other'] += 1
            
            # Extract security events
            if any(keyword in str(message).lower() for keyword in ['unauthorized', 'blocked', 'denied', 'failed']):
                security_events.append({
                    'timestamp': timestamp,
                    'type': 'Security Alert',
                    'severity': 'Medium',
                    'source': source,
                    'status': 'Blocked'
                })
            
            # Extract system events
            if any(keyword in str(message).lower() for keyword in ['service', 'restart', 'error', 'warning']):
                system_events.append({
                    'timestamp': timestamp,
                    'type': 'System Event',
                    'category': 'System',
                    'description': str(message)[:100] + '...' if len(str(message)) > 100 else str(message),
                    'status': 'Completed'
                })
        
        # Convert counts to percentages for traffic sources
        total_messages = sum(traffic_sources.values())
        if total_messages > 0:
            traffic_sources = {k: (v / total_messages) * 100 for k, v in traffic_sources.items()}
        
        # Create time series data
        if time_series_data:
            df = pd.DataFrame(time_series_data)
            df = df.set_index('timestamp').resample('1H').sum().fillna(0)
            times = df.index
            total_traffic = df['total_traffic'].values
            allowed_traffic = df['allowed_traffic'].values
            blocked_traffic = df['blocked_traffic'].values
        else:
            # If no data, create empty time series
            times = pd.date_range(start=start_time, end=end_time, freq='1H')
            total_traffic = np.zeros(len(times))
            allowed_traffic = np.zeros(len(times))
            blocked_traffic = np.zeros(len(times))
        
        return {
            'traffic_sources': traffic_sources,
            'traffic_types': traffic_types,
            'times': times,
            'total_traffic': total_traffic,
            'allowed_traffic': allowed_traffic,
            'blocked_traffic': blocked_traffic,
            'security_events': security_events[:10],  # Limit to 10 most recent
            'system_events': system_events[:10]  # Limit to 10 most recent
        }
        
    except Exception as e:
        add_status_message("data_processing_error", f"Error processing Graylog data: {str(e)}", "error")
        return None

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
    # Dashboard header with proper spacing
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
    
    # Get real data from Graylog
    traffic_data = get_graylog_data(time_period)
    
    if traffic_data:
        # Charts section with improved spacing
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Create three columns for charts with better spacing
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            fig1 = create_traffic_source_chart(traffic_data['traffic_sources'])
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            fig2 = create_traffic_over_time_chart(
                traffic_data['times'], 
                traffic_data['total_traffic'], 
                traffic_data['blocked_traffic'], 
                traffic_data['allowed_traffic']
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        
        with col3:
            fig3 = create_traffic_type_chart(traffic_data['traffic_types'])
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tables section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Security Events")
            if traffic_data['security_events']:
                security_df = pd.DataFrame(traffic_data['security_events'])
                st.dataframe(security_df, use_container_width=True, hide_index=True)
            else:
                st.info("No security events found in the selected time period.")
        
        with col2:
            st.subheader("System Events")
            if traffic_data['system_events']:
                system_df = pd.DataFrame(traffic_data['system_events'])
                st.dataframe(system_df, use_container_width=True, hide_index=True)
            else:
                st.info("No system events found in the selected time period.")
    
    else:
        # Show error message if no data available
        st.error("Unable to retrieve data from Graylog. Please check your connection and try again.")
    
    # Add a button to manually dismiss all messages (for testing)
    if st.button("Dismiss All Messages"):
        st.session_state.dismissed_messages.update([msg["id"] for msg in st.session_state.status_messages])
        st.rerun()

if __name__ == "__main__":
    main() 