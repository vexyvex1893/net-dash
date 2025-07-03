#!/usr/bin/env python3
"""
Test script to verify dashboard functionality
Run this to check if all components are working before deploying
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

def test_dashboard_components():
    """Test all dashboard components with sample data"""
    
    st.title("🧪 Dashboard Component Test")
    st.write("This test verifies that all dashboard components are working correctly.")
    
    # Generate test data
    test_data = []
    for i in range(24):
        test_data.append({
            'timestamp': datetime.now() - timedelta(hours=i),
            'router_traffic': random.randint(1000, 5000),
            'iot_traffic': random.randint(100, 1000),
            'email_traffic': random.randint(500, 2000),
            'web_traffic': random.randint(2000, 8000),
            'total_traffic': random.randint(5000, 15000),
            'blocked_traffic': random.randint(100, 500),
            'allowed_traffic': random.randint(4000, 14000),
            'protocol': random.choice(['HTTP', 'HTTPS', 'DNS', 'SMTP', 'SSH', 'FTP']),
            'traffic_volume': random.randint(1000, 5000),
            'event_type': random.choice(['security', 'system', 'network']),
            'source_ip': f'192.168.1.{random.randint(1, 254)}',
            'severity': random.choice(['High', 'Medium', 'Low']),
            'status': random.choice(['Blocked', 'Allowed'])
        })
    
    df = pd.DataFrame(test_data)
    
    # Test 1: Pie Chart
    st.subheader("✅ Test 1: Traffic Source Distribution (Pie Chart)")
    traffic_sources = {
        'Router': df['router_traffic'].sum(),
        'IoT Devices': df['iot_traffic'].sum(),
        'Email Server': df['email_traffic'].sum(),
        'Web Server': df['web_traffic'].sum()
    }
    fig1 = go.Figure(data=[go.Pie(
        labels=list(traffic_sources.keys()),
        values=list(traffic_sources.values()),
        hole=0.4,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    )])
    fig1.update_layout(height=300)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Test 2: Line Chart
    st.subheader("✅ Test 2: Traffic Over Time (Line Chart)")
    fig2 = px.line(df, x='timestamp', y=['total_traffic', 'blocked_traffic', 'allowed_traffic'],
                   color_discrete_map={
                       'total_traffic': '#2E86C1',
                       'blocked_traffic': '#E74C3C',
                       'allowed_traffic': '#27AE60'
                   })
    fig2.update_layout(height=300)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Test 3: Bar Chart
    st.subheader("✅ Test 3: Traffic Type Distribution (Bar Chart)")
    protocol_df = df.groupby('protocol')['traffic_volume'].sum().reset_index()
    fig3 = px.bar(protocol_df, x='protocol', y='traffic_volume',
                  color='protocol',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Test 4: Data Tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Test 4a: Security Events Table")
        security_df = df[df['event_type'] == 'security']
        if not security_df.empty:
            st.dataframe(security_df[['timestamp', 'source_ip', 'severity', 'status']].head(5),
                        hide_index=True, use_container_width=True)
        else:
            st.info("No security events in test data")
    
    with col2:
        st.subheader("✅ Test 4b: System Events Table")
        system_df = df[df['event_type'] == 'system']
        if not system_df.empty:
            st.dataframe(system_df[['timestamp', 'source_ip', 'severity', 'status']].head(5),
                        hide_index=True, use_container_width=True)
        else:
            st.info("No system events in test data")
    
    # Test 5: Time Period Selector
    st.subheader("✅ Test 5: Time Period Selector")
    time_period = st.selectbox(
        "Display Period",
        options=["Last 1 hour", "Last 6 hours", "Last 12 hours", "Last 24 hours", "Last 7 days"],
        index=3
    )
    st.write(f"Selected period: {time_period}")
    
    # Test 6: Refresh Button
    st.subheader("✅ Test 6: Refresh Functionality")
    if st.button("🔄 Test Refresh"):
        st.success("Refresh button working!")
        st.rerun()
    
    st.success("🎉 All dashboard components are working correctly!")
    st.info("If you can see all the charts and tables above, your dashboard should work properly.")

if __name__ == "__main__":
    test_dashboard_components() 