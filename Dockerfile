FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY enhanced_network_dashboard.py .

EXPOSE 8501

CMD ["streamlit", "run", "enhanced_network_dashboard.py", "--server.address=0.0.0.0"]