#!/bin/bash

echo "🚀 Deploying Network Dashboard Updates..."

# Check if we're in the right directory
if [ ! -f "network_dashboard.py" ]; then
    echo "❌ Error: network_dashboard.py not found in current directory"
    echo "Please run this script from the dashboard directory"
    exit 1
fi

# Update requirements if needed
echo "📦 Checking requirements..."
if [ -f "requirements.txt" ]; then
    echo "✅ Requirements file found"
else
    echo "❌ Requirements file missing"
    exit 1
fi

# Test the dashboard locally first
echo "🧪 Testing dashboard components..."
python -c "
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import requests
print('✅ All imports successful')
"

if [ $? -eq 0 ]; then
    echo "✅ Dashboard test passed"
else
    echo "❌ Dashboard test failed - check your Python environment"
    exit 1
fi

# If using Docker, rebuild the container
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Rebuilding Docker container..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Docker container rebuilt and started"
elif [ -f "Dockerfile" ]; then
    echo "🐳 Building Docker image..."
    docker build -t network-dashboard .
    echo "✅ Docker image built"
    echo "To run: docker run -p 8501:8501 network-dashboard"
else
    echo "📝 No Docker configuration found - using direct Python execution"
    echo "To run: streamlit run network_dashboard.py"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Test the dashboard: streamlit run test_dashboard.py"
echo "2. Run the main dashboard: streamlit run network_dashboard.py"
echo "3. Check that all 3 graphs and 2 event tables are visible"
echo "4. Verify the time period selector works"
echo "5. Test the refresh functionality"
echo ""
echo "If using Docker, the dashboard should be available at:"
echo "http://your-server-ip:8501" 