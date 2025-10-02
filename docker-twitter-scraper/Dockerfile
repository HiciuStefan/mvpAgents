# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Firefox and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    firefox-esr \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install webdriver-manager for FirefoxDriver management
RUN pip install webdriver-manager

# Install FirefoxDriver manually
RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz && \
    tar -xzf /tmp/geckodriver.tar.gz -C /tmp/ && \
    mv /tmp/geckodriver /usr/local/bin/geckodriver && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# Set environment variables for Firefox
ENV DISPLAY=:99
ENV FIREFOX_BIN=/usr/bin/firefox-esr
ENV GECKODRIVER_PATH=/usr/local/bin/geckodriver

# Default command
CMD ["python", "twitter_scraper.py"]

