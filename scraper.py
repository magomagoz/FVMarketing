import requests

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    payload = {
        "q": f"{query} sede legale città fatturato sito:reportaziende.it OR sito:ufficiocamerale.it",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snippet = res.get('snippet', '')
            title = res.get('title', '')
            piva_match = re.search(r'\b\d{11}\b', f"{title} {snippet}")
            if piva_match:
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                
                # Pulizia città per evitare "LEGALE Me..." visto negli screenshot
                citta_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', snippet)
                citta = citta_match.group(1) if citta_match else "Da verificare"
                if "LEGALE" in citta.upper(): citta = "Verifica Sede"

                companies.append({
                    "name": title.split(' - ')[0].split('|')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": citta,
                    "revenue": rev_match.group(0) if rev_match else "Dato non disp."
                })
        return companies
    except: return []

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
