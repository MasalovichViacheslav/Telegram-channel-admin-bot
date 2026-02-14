# Use official Python 3.12 image (slim version)
FROM python:3.12-slim

# Set environment variables
# PYTHONUNBUFFERED=1 - logs are output immediately without buffering
# PLAYWRIGHT_BROWSERS_PATH - where Playwright will store browsers
ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies for Chromium
# These are libraries required for browser to run in headless mode
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxshmfence1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in container
WORKDIR /app

# Copy requirements file
# Copy separately to cache this layer
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium without system dependencies
# We already installed all necessary dependencies manually above
RUN playwright install chromium

# Copy all application code to container
COPY . .

# Set Minsk timezone for correct timestamps
ENV TZ=Europe/Minsk
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Application startup command
CMD ["python", "main.py"]
