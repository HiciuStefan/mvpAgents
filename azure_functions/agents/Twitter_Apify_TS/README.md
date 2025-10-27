# Twitter Apify Scraper - TypeScript Version

Azure Function pentru scraping Twitter folosind Apify API, scris în TypeScript.

## Features

- 🔄 Scraping tweets prin Apify Twitter Scraper V2
- 📊 Integrare cu Supabase pentru configurare dinamică
- 💾 Salvare automată a rezultatelor în JSON
- ⚡ Async/await pentru performanță optimă
- 🛡️ Type safety cu TypeScript
- 🔐 Azure Functions authentication level

## Prerequisite

- Node.js 18.x sau mai nou
- npm sau yarn
- Azure Functions Core Tools v4
- Cont Apify cu API token
- Cont Supabase (opțional, pentru configurare dinamică)

## Instalare

```bash
# Instalează dependențele
npm install

# Compilează TypeScript
npm run build
```

## Configurare

Creează fișierul `local.settings.json` (sau editează-l):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "node",
    "APIFY_TOKEN": "your_apify_token",
    "SUPABASE_URL": "your_supabase_url",
    "SUPABASE_SERVICE_ROLE_KEY": "your_supabase_key"
  }
}
```

## Rulare locală

```bash
# Start function app
npm start
```

Function-ul va fi disponibil la: `http://localhost:7071/api/scrape_twitter`

## Utilizare

### Request Body

```json
{
  "username": "lica2216",
  "max_posts": 20,
  "search_type": "Top"
}
```

**Parametri:**
- `username` (opțional): Username-ul Twitter de scanat. Dacă lipsește, se va încerca preluarea din Supabase.
- `max_posts` (opțional, default: 20): Numărul maxim de tweet-uri de returnat.
- `search_type` (opțional, default: "Top"): Tipul de căutare ("Top" sau "Latest").

### Response

```json
{
  "success": true,
  "count": 20,
  "tweets": [
    {
      "tweet_id": "123456789",
      "url": "https://twitter.com/user/status/123456789",
      "text": "Tweet content...",
      "author": "username",
      "created_at": "2024-01-01T12:00:00Z",
      "likes": 100,
      "retweets": 50,
      "replies": 25,
      "views": "1000"
    }
  ]
}
```

### Exemplu cURL

```bash
curl -X POST http://localhost:7071/api/scrape_twitter \
  -H "Content-Type: application/json" \
  -d '{
    "username": "lica2216",
    "max_posts": 20,
    "search_type": "Top"
  }'
```

## Structura proiectului

```
Twitter_Apify_TS/
├── src/
│   ├── functions/
│   │   └── scrapeTwitter.ts    # Azure Function endpoint
│   ├── supabaseRetriever.ts    # Supabase integration
│   └── types.ts                 # TypeScript type definitions
├── dist/                        # Compiled JavaScript (generated)
├── package.json
├── tsconfig.json
├── host.json
├── local.settings.json
└── README.md
```

## Development

```bash
# Watch mode pentru development
npm run watch

# În alt terminal, rulează function app
npm start

# Clean build artifacts
npm run clean
```

## Deployment pe Azure

1. Asigură-te că ai Azure CLI instalat și autentificat
2. Creează o Function App în Azure Portal
3. Configurează variabilele de mediu în Azure Portal
4. Deploy:

```bash
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```

## Diferențe față de versiunea Python

- ✅ Type safety cu TypeScript
- ✅ Axios în loc de requests
- ✅ Promises/async-await nativ
- ✅ Better error handling cu typed exceptions
- ✅ Supabase JS client oficial
- ✅ Modern ES modules și TypeScript features

## Troubleshooting

### Function nu pornește
- Verifică că ai instalat Azure Functions Core Tools v4
- Rulează `npm install` și `npm run build`

### Timeout errors
- Crește `TIMEOUT_SECONDS` în cod dacă e necesar
- Verifică conexiunea la Apify API

### Supabase errors
- Verifică că variabilele SUPABASE_URL și SUPABASE_SERVICE_ROLE_KEY sunt setate corect
- Verifică că tabela `items` există și conține itemul `twitter_config`

## License

MIT


