import requests

def fetch_company_news(company_name):
    print(f"[DEBUG] Fetching news for: {company_name}")

    if not company_name or company_name.strip() == "":
        return "❌ No company name provided for news search."

    NEWS_API_KEY = "pub_8916b0849afa4ac18151c762241a2075"

    query = f'"{company_name}" AND (finance OR earnings OR strategy OR acquisition)'

    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWS_API_KEY,
        "q": query,
        "language": "en",
        "country": "au",
        "category": "business"
    }

    try:
        response = requests.get(url, params=params)
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Body: {response.text[:500]}")  # Truncated

        if response.status_code != 200:
            return f"❌ Error fetching news: {response.status_code} - {response.text}"

        data = response.json()
        articles = data.get("results", [])

        # Post-filter for higher relevance
        filtered = [
            a for a in articles
            if company_name.lower() in a.get("title", "").lower() 
            or company_name.lower() in a.get("description", "").lower()
        ]

        if not filtered:
            return "No relevant articles found."

        output = "\n\n".join([
            f"• {a.get('title')}\n  {a.get('link', '')}"
            for a in filtered[:3]
        ])
        return output

    except Exception as e:
        return f"❌ Exception during news fetch: {e}"

