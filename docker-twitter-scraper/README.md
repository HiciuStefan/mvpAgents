# Twitter Scraper Docker Setup

## Quick Start

### 1. Build and run with Docker Compose (recommended)
```bash
# Copy your .env file to this directory
cp ../.env .env

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### 2. Build and run manually
```bash
# Build the image
docker build -t twitter-scraper .

# Run the container
docker run -d \
  --name twitter-scraper \
  --env-file .env \
  -v $(pwd)/scraped_tweets.json:/app/scraped_tweets.json \
  -v $(pwd)/scraping_state.json:/app/scraping_state.json \
  twitter-scraper

# View logs
docker logs -f twitter-scraper

# Stop the container
docker stop twitter-scraper
docker rm twitter-scraper
```

### 3. Run once (for testing)
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/scraped_tweets.json:/app/scraped_tweets.json \
  -v $(pwd)/scraping_state.json:/app/scraping_state.json \
  twitter-scraper
```

## Environment Variables

Create a `.env` file with:
```
TWITTER_USER=your_twitter_username
TWITTER_PASS=your_twitter_password
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Volumes

The container mounts these files to persist data:
- `scraped_tweets.json` - Contains all scraped tweets
- `scraping_state.json` - Contains the last scraped tweet ID
- `twitter_config_fallback.json` - Fallback configuration

## Scheduling

The Docker Compose setup runs the scraper every 30 minutes automatically. You can modify the schedule by changing the `sleep` value in `docker-compose.yml`.

## Troubleshooting

### View container logs
```bash
docker-compose logs -f twitter-scraper
```

### Access container shell
```bash
docker exec -it twitter-scraper bash
```

### Rebuild after code changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Features

- **Dockerized**: Runs in a containerized environment
- **Headless Chrome**: Optimized for server environments
- **Incremental Scraping**: Only scrapes new tweets since last run
- **Persistent State**: Maintains scraping state between runs
- **Automatic Scheduling**: Runs every 30 minutes
- **Error Handling**: Robust error handling and retry logic
- **Logging**: Comprehensive logging for debugging





