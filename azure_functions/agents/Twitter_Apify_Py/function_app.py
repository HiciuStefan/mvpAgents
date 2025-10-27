import azure.functions as func
import logging
import json
import os
import requests
from supabase_retriever import get_monitored_twitter_usernames

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Apify API Configuration
APIFY_ACTOR_ID = "ghSpYIW3L1RvT57NT"  # Twitter Scraper V2
APIFY_API_BASE = "https://api.apify.com/v2"
TIMEOUT_SECONDS = 300  # 5 minutes for sync request


@app.route(route="scrape_twitter", auth_level=func.AuthLevel.FUNCTION, methods=["POST"]) 
def scrape_twitter(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simple Twitter scraper endpoint using Apify.
    
    POST body example:
    {
        "username": "lica2216",
        "max_posts": 20,
        "search_type": "Top"
    }
    """
    logging.info('Twitter scraper endpoint called')
    
    # Get Apify token from environment
    apify_token = os.getenv("APIFY_TOKEN")
    if not apify_token:
        return func.HttpResponse(
            json.dumps({"error": "APIFY_TOKEN not configured"}),
            status_code=500,
            mimetype="application/json"
        )
    
    # Parse request body
    try:
        req_body = req.get_json()
    except ValueError:
        req_body = {}
    
    # Get username: from request body, or from Supabase, or fallback to hardcoded
    username = req_body.get("username")
    
    if not username:
        # Try to get from Supabase
        logging.info("No username in request, fetching from Supabase...")
        try:
            usernames = get_monitored_twitter_usernames()
            if usernames:
                username = usernames[0]  # Use first monitored username
                logging.info(f"Found username from Supabase: {username}")
            else:
                username = "lica2216"  # Final fallback
                logging.warning("No usernames in Supabase, using fallback: lica2216")
        except Exception as e:
            logging.error(f"Failed to get usernames from Supabase: {e}")
            username = "lica2216"  # Fallback on error
    
    # Build actor input - use exact parameters that work in Apify console
    actor_input = {
        "username": username,
        "max_posts": req_body.get("max_posts", 20),
        "search_type": req_body.get("search_type", "Top")
    }
    
    logging.info(f'Running Apify scraper with input: {actor_input}')
    
    # Call Apify API (sync mode - wait for results)
    try:
        url = f"{APIFY_API_BASE}/acts/{APIFY_ACTOR_ID}/run-sync-get-dataset-items"
        headers = {
            "Authorization": f"Bearer {apify_token}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            url, 
            headers=headers, 
            json=actor_input, 
            timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        
        # Get results
        items = response.json()
        if not isinstance(items, list):
            items = [items] if items else []
        
        # Filter out demo items and normalize
        tweets = []
        for item in items:
            if item.get("demo"):
                continue
            
            # Extract author info
            author = item.get("author", {})
            author_name = author.get("screen_name", "") or author.get("name", "")
            tweet_id = item.get("tweet_id", "")
            
            # Build tweet URL
            tweet_url = f"https://twitter.com/{author_name}/status/{tweet_id}" if author_name and tweet_id else ""
                
            tweets.append({
                "tweet_id": str(tweet_id),
                "url": tweet_url,
                "text": item.get("text", ""),
                "author": author_name,
                "created_at": item.get("created_at", ""),
                "likes": item.get("favorites", 0),
                "retweets": item.get("retweets", 0),
                "replies": item.get("replies", 0),
                "views": item.get("views", "0"),
            })
        
        logging.info(f'Successfully scraped {len(tweets)} tweets')
        
        # Save results to local JSON file
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(script_dir, "scraped_tweets.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, indent=2, ensure_ascii=False)
            logging.info(f'Saved {len(tweets)} tweets to {output_path}')
        except Exception as e:
            logging.warning(f'Failed to save tweets to file: {str(e)}')
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "count": len(tweets),
                "tweets": tweets
            }, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except requests.exceptions.Timeout:
        logging.error("Apify request timed out")
        return func.HttpResponse(
            json.dumps({"error": "Request timed out after 5 minutes"}),
            status_code=504,
            mimetype="application/json"
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Apify request failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Scraper failed: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Unexpected error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
