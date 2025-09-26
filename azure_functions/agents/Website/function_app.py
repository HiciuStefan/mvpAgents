import azure.functions as func
import logging
import json
import os
import sys

# Ensure project root is on path for shared utilities in `agents/_tools`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import local scraper entrypoint for the Azure Function app
from article_scraper import ArticleScraperV3

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="article_scraper", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def article_scraper_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function for article_scraper processed a request.')

    try:
        req_body = req.get_json()
        base_url = req_body.get("base_url")
        client_name = req_body.get("client_name")
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body."}),
            status_code=400,
            mimetype="application/json"
        )

    if not base_url or not client_name:
        return func.HttpResponse(
            json.dumps({"error": "Please provide 'base_url' and 'client_name' in the request body."}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        scraper = ArticleScraperV3()
        scraper.run(base_url, client_name)
        
        return func.HttpResponse(
            json.dumps({"status": "success", "message": f"Scraping initiated for {client_name} at {base_url}."}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
