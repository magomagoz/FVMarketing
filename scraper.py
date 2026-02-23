import requests

def search_decision_maker(company_name):
    # Eseguiamo una ricerca mirata su Google via API
    # Query: "Direttore Generale [Nome Azienda] LinkedIn"
    api_key = "TUO_SERPAPI_KEY"
    query = f"Direttore Generale {company_name} LinkedIn"
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }
    
    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json().get("organic_results", [])
    
    if results:
        # Il primo risultato solitamente è il profilo più rilevante
        top_result = results[0]
        return {
            "name": top_result.get("title").split("-")[0].strip(),
            "profile_url": top_result.get("link")
        }
    return None
