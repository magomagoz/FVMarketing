import requests

def search_company_list(query):
    """Cerca aziende su Google via Serper filtrando per database italiani."""
    search_url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': 'TUA_CHIAVE_SERPER', # Assicurati che sia nei Secrets!
        'Content-Type': 'application/json'
    }
    payload = {
        "q": f"{query} sito:ufficiocamerale.it OR sito:reportaziende.it",
        "gl": "it", "hl": "it"
    }
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            # Pulizia del titolo per avere Nome + Località
            title = res.get('title', '').split('|')[0].split(' - ')[0]
            companies.append({
                "name": title,
                "location": res.get('snippet', 'Località non specificata'),
                "link": res.get('link')
            })
        return companies[:5]
    except:
        return []

def search_decision_maker(company_name):
    """Cerca il DG o Titolare per l'azienda selezionata."""
    # ... (mantieni la tua logica precedente qui) ...
    return [{"name": "Direttore Generale", "source": "Ricerca generica", "link": "#", "snippet": "Contatto standard"}]
