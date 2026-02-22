import requests

def search_company_list(query):
    """Cerca una lista di aziende potenziali con località."""
    search_url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': 'TUA_CHIAVE_SERPER', # Inseriscila nei Secrets
        'Content-Type': 'application/json'
    }
    # Cerchiamo su database aziendali italiani per avere la località
    payload = {
        "q": f"{query} sito:ufficiocamerale.it OR sito:reportaziende.it",
        "gl": "it", "hl": "it"
    }
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            title = res.get('title', '').split('|')[0].split(' - ')[0]
            # Estraiamo la località dallo snippet
            companies.append({
                "name": title,
                "info": res.get('snippet', 'Località non trovata'),
                "link": res.get('link')
            })
        return companies[:5]
    except Exception as e:
        print(f"Errore ricerca: {e}")
        return []

def search_decision_maker(company_name):
    """Cerca i Decision Maker per l'azienda scelta."""
    # Tua logica di ricerca LinkedIn/Google
    return [{"name": "Direttore Generale", "source": "LinkedIn", "link": "#", "snippet": "Profilo trovato"}]
