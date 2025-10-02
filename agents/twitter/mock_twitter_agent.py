import json
import os
from agents._tools.llm_twitterAgent import classify_tweet
from agents.common.api_sender import ApiClient
from agents.twitter.payload_builder import build_twitter_payload
from agents.common.json_validator import validate_json
from pathlib import Path


def load_mock_tweets_from_scenarios() -> list:
    """
    Încarcă tweet-urile mock din context/scenarios/twitter_scraped.json
    """
    try:
        # Calea către fișierul de scenarios
        project_root = Path(__file__).parent.parent.parent
        scenarios_file = project_root / "context" / "scenarios" / "twitter_scraped.json"
        
        if not scenarios_file.exists():
            print(f"⚠️ Fișierul de scenarios nu există: {scenarios_file}")
            print("Creează mai întâi tweet-uri cu scrape_tweets.py")
            return []
        
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            mock_tweets = json.load(f)
        
        print(f"✅ Încărcat {len(mock_tweets)} tweet-uri mock din scenarios")
        return mock_tweets
        
    except Exception as e:
        print(f"❌ Eroare la încărcarea tweet-urilor mock: {e}")
        return []


def create_fallback_mock_tweets() -> list:
    """
    Creează tweet-uri mock de test dacă nu există fișierul scenarios
    """
    fallback_tweets = [
        {
            "type": "twitter",
            "client_name": "SolarisProAi",
            "tweet_id": "1234567890",
            "url": "https://twitter.com/solarisproai/status/1234567890",
            "content": "Exciting news! We're launching our new AI-powered solution next week. Stay tuned for updates! #AI #Innovation #TechNews"
        },
        {
            "type": "twitter", 
            "client_name": "ClientA",
            "tweet_id": "1234567891",
            "url": "https://twitter.com/clienta/status/1234567891",
            "content": "Looking for AI developers to join our team. Experience with NLP and machine learning required. DM us if interested! #Hiring #AI #Jobs"
        },
        {
            "type": "twitter",
            "client_name": "ClientB", 
            "tweet_id": "1234567892",
            "url": "https://twitter.com/clientb/status/1234567892",
            "content": "Great meeting with @solarisproai today! Their AI solutions are exactly what we need for our digital transformation. #Partnership #AI #DigitalTransformation"
        }
    ]
    
    print(f"✅ Creați {len(fallback_tweets)} tweet-uri mock de fallback")
    return fallback_tweets


def main():
    """
    Rulează agentul Twitter cu date mock din scenarios
    """
    print("🚀 Rulăm Twitter Agent cu date mock...")
    
    # Încarcă tweet-urile mock
    mock_tweets = load_mock_tweets_from_scenarios()
    
    # Dacă nu există scenarios, folosește fallback
    if not mock_tweets:
        mock_tweets = create_fallback_mock_tweets()
    
    if not mock_tweets:
        print("❌ Nu s-au putut încărca tweet-uri mock. Oprire.")
        return {}
    
    # Inițializează clientul API
    try:
        twitter_api_client = ApiClient(
            api_endpoint_env="TWITTER_AGENT_URL",
            api_key_env="TWITTER_AGENT_API_KEY"
        )
        print("✅ Client API Twitter inițializat")
    except Exception as e:
        print(f"⚠️ Nu s-a putut inițializa clientul API: {e}")
        print("Continuăm cu procesarea locală...")
        twitter_api_client = None
    
    # Procesează fiecare tweet mock
    processed_tweets = []
    for i, tweet in enumerate(mock_tweets, 1):
        print(f"\n📱 Procesez tweet {i}/{len(mock_tweets)}: {tweet.get('content', '')[:50]}...")
        
        # Analizează tweet-ul cu LLM
        try:
            classification = classify_tweet(
                tweet.get("content", ""), 
                client_name=tweet.get("client_name")
            )
            print(f"  ✅ Analiză LLM: {classification.get('short_description', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Eroare analiză LLM: {e}")
            continue
        
        # Construiește payload-ul
        try:
            payload = build_twitter_payload(tweet, classification)
            processed_tweets.append(payload)
            print(f"  ✅ Payload construit pentru {payload.get('client_name', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Eroare construire payload: {e}")
            continue
    
    if not processed_tweets:
        print("❌ Nu s-au putut procesa tweet-urile. Oprire.")
        return {}
    
    print(f"\n📊 Procesare completă: {len(processed_tweets)} tweet-uri procesate")
    
    # Salvează rezultatele procesate în scenarios pentru context agent
    try:
        project_root = Path(__file__).parent.parent.parent
        output_file = project_root / "context" / "scenarios" / "twitter_processed.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_tweets, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Rezultatele procesate salvate în: {output_file}")
    except Exception as e:
        print(f"⚠️ Nu s-au putut salva rezultatele: {e}")
    
    # Trimite la API dacă este disponibil
    if twitter_api_client:
        print(f"\n🌐 Se încearcă trimiterea a {len(processed_tweets)} tweet-uri către API...")
        
        # Încarcă schema pentru validare
        try:
            schema_file = Path(__file__).parent / ".." / "config" / "twitter_schema.json"
            with open(schema_file, 'r') as f:
                tweet_schema = json.load(f)
        except Exception as e:
            print(f"⚠️ Nu s-a putut încărca schema: {e}")
            tweet_schema = None
        
        successful_sends = 0
        for tweet in processed_tweets:
            try:
                # Validează dacă schema este disponibilă
                if tweet_schema:
                    is_valid, message = validate_json(tweet, tweet_schema)
                    if not is_valid:
                        print(f"  ❌ Tweet invalid: {message}")
                        continue
                
                # Trimite la API
                if twitter_api_client.send_data(tweet):
                    successful_sends += 1
                    print(f"  ✅ Tweet trimis cu succes: {tweet.get('short_description', 'N/A')}")
                else:
                    print(f"  ❌ Eroare la trimiterea tweet-ului")
                    
            except Exception as e:
                print(f"  ❌ Eroare la procesarea tweet-ului: {e}")
        
        print(f"\n📈 Rezumat trimitere: {successful_sends} din {len(processed_tweets)} tweet-uri trimise cu succes")
    else:
        print("\n⚠️ Client API indisponibil - tweet-urile nu au fost trimise")
    
    print("\n🎉 Twitter Agent Mock finalizat cu succes!")
    return {"processed_tweets": len(processed_tweets)}


if __name__ == "__main__":
    main()

