import requests

def search_company_list(query):
    """Cerca una lista di aziende corrispondenti al nome inserito."""
    search_url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': 'TUA_CHIAVE_SERPER',
        'Content-Type': 'application/json'
    }
    # Forziamo la ricerca su siti che riportano dati aziendali italiani
    payload = {
        "q": f"{query} sito:ufficiocamerale.it OR sito:reportaziende.it",
        "gl": "it",
        "hl": "it"
    }
    
    response = requests.post(search_url, json=payload, headers=headers)
    results = response.json().get('organic', [])
    
    companies = []
    for res in results:
        # Estraiamo nome e località dallo snippet o dal titolo
        title = res.get('title', '')
        snippet = res.get('snippet', '')
        link = res.get('link', '')
        
        # Filtriamo solo risultati che sembrano aziende reali
        if "P.IVA" in snippet or "-" in title:
            companies.append({
                "display_name": f"{title}",
                "link": link,
                "snippet": snippet
            })
            
    return companies[:5] # Restituiamo le prime 5 corrispondenze
