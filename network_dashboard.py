import streamlit as st
import psutil
import time
import plotly.graph_objects as go
from datetime import datetime

st.title("Network Traffic Dashboard")

def get_network_usage():
    # Get network statistics
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent, net_io.bytes_recv

def main():
    st.write("Monitoring network traffic...")
    
    # Initialize placeholder for the chart
    chart_placeholder = st.empty()
    
    # Initialize data lists
    times = []
    sent_data = []
    recv_data = []
    
    while True:
        # Get current time
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Get network usage
        bytes_sent, bytes_recv = get_network_usage()
        
        # Append data
        times.append(current_time)
        sent_data.append(bytes_sent / 1024 / 1024)  # Convert to MB
        recv_data.append(bytes_recv / 1024 / 1024)  # Convert to MB
        
        # Create the graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=sent_data, name='Sent (MB)'))
        fig.add_trace(go.Scatter(x=times, y=recv_data, name='Received (MB)'))
        
        fig.update_layout(
            title='Network Traffic Over Time',
            xaxis_title='Time',
            yaxis_title='Data (MB)',
            height=600
        )
        
        # Update the chart
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Keep only last 50 data points
        if len(times) > 50:
            times = times[-50:]
            sent_data = sent_data[-50:]
            recv_data = recv_data[-50:]
        
        time.sleep(1)

if __name__ == "__main__":
    main() 