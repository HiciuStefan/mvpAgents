import azure.functions as func
import logging
import json
import os
import sys

# Ensure project root is on path for shared utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from twitter_scraper import TwitterScraper

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="twitter_scraper", auth_level=func.AuthLevel.FUNCTION, methods=["POST"]) 
def twitter_scraper_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger for twitter_scraper received a request.')

    try:
        req_body = req.get_json()
        headless = bool(req_body.get("headless", True)) if isinstance(req_body, dict) else True
    except ValueError:
        headless = True

    try:
        scraper = TwitterScraper(headless=headless)
        tweets = scraper.run()
        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "found": len(tweets or []),
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error during Twitter scraping: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


