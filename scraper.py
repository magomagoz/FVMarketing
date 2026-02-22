import requests
import streamlit as st

def search_company_list(query):
    """Cerca aziende con località usando Serper."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    
    if not api_key:
        return [{"name": "Errore", "location": "Manca API KEY nei Secrets", "link": ""}]

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Query ottimizzata per trovare sedi legali e siti di report aziendali
    payload = {
        "q": f"{query} sede legale sito:ufficiocamerale.it OR sito:reportaziende.it",
        "gl": "it",
        "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        
        companies = []
        for res in results:
            title = res.get('title', '').split(' - ')[0].split(' | ')[0]
            companies.append({
                "name": title,
                "location": res.get('snippet', 'Località non disponibile')[:100],
                "link": res.get('link')
            })
        return companies if companies else []
    except Exception as e:
        return []

def search_decision_maker(company_name):
    """Cerca il DG/Titolare."""
    # Mock semplice per evitare altri errori di importazione
    return [{"name": "Direttore Generale", "source": "LinkedIn", "link": "#", "snippet": "Profilo individuato"}]
