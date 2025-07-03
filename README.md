# Network Traffic Monitoring Dashboard

A modern, interactive dashboard for monitoring network traffic across various devices and connections in your office network.

## Features

- Real-time network traffic monitoring
- Device-wise traffic distribution
- Network activity timeline
- Recent network events log
- Time period selection (Last Hour, 6 Hours, 24 Hours, Week)
- Detailed device statistics
- Interactive visualizations

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the dashboard:
```bash
streamlit run network_dashboard.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Dashboard Components

- **Top Metrics**: Shows total network traffic, active connections, and network health
- **Traffic Distribution**: Pie chart showing traffic distribution across devices
- **Network Timeline**: Line chart showing network activity over time
- **Network Events**: Log of recent network events and activities
- **Device Details**: Table showing detailed statistics for each device

## Customization

You can modify the following aspects of the dashboard:

- Time periods in the sidebar
- Device list in the mock data generator
- Event types and severity levels
- Chart types and visualizations
- CSS styling

## Note

This version uses mock data for demonstration. To use real network data, you'll need to:

1. Implement actual network monitoring using libraries like `psutil` or `scapy`
2. Set up proper network permissions
3. Configure your network devices to allow monitoring
4. Replace the mock data generation with real-time data collection

## Requirements

- Python 3.7+
- Streamlit
- Plotly
- Pandas
- psutil
- scapy
- python-dotenv 