#!/bin/bash

# Quick start script for Twitter Scraper Docker

echo "🚀 Starting Twitter Scraper Docker..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
TWITTER_USER=your_twitter_username
TWITTER_PASS=your_twitter_password
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
EOF
    echo "📝 Please edit .env file with your credentials and run this script again."
    exit 1
fi

# Build and start
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting container..."
docker-compose up -d

echo "📊 Container status:"
docker-compose ps

echo ""
echo "📋 Useful commands:"
echo "  docker-compose logs -f     # View logs"
echo "  docker-compose down        # Stop container"
echo "  docker-compose restart     # Restart container"
echo ""
echo "✅ Twitter Scraper is running!"










