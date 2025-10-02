#!/bin/bash

# Twitter Scraper Docker Test Script

echo "🐳 Testing Twitter Scraper Docker Setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your credentials:"
    echo "TWITTER_USER=your_username"
    echo "TWITTER_PASS=your_password"
    echo "SUPABASE_URL=your_supabase_url"
    echo "SUPABASE_KEY=your_supabase_key"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo "✅ .env file found"

# Build the image
echo "🔨 Building Docker image..."
docker build -t twitter-scraper .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Test run (single execution)
echo "🧪 Testing single run..."
docker run --rm \
    --env-file .env \
    -v $(pwd)/scraped_tweets.json:/app/scraped_tweets.json \
    -v $(pwd)/scraping_state.json:/app/scraping_state.json \
    twitter-scraper

if [ $? -eq 0 ]; then
    echo "✅ Single run test successful"
else
    echo "❌ Single run test failed"
    exit 1
fi

echo "🎉 All tests passed! You can now run:"
echo "   docker-compose up -d    # Start the scraper"
echo "   docker-compose logs -f  # View logs"
echo "   docker-compose down     # Stop the scraper"





