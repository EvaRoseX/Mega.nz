# Base image standard python use karenge
FROM python:3.11-slim

# System me FFmpeg aur baaki tools install karne ke liye
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Working directory set karenge
WORKDIR /app

# Requirements file copy karke dependencies install karenge
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Poora code copy karenge
COPY . .

# Flask application port expose karenge
EXPOSE 8080

# Bot run karne ki command
CMD ["python", "bot.py"]
