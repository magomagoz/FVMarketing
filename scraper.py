import requests
import streamlit as st

def search_company_list(query):
    """Cerca aziende in modo elastico su Google via Serper."""
    search_url = "https://google.serper.dev/search"
    
    # Recupera la chiave dai Secrets (Assicurati che si chiami SERPER_API_KEY)
    api_key = st.secrets.get("SERPER_API_KEY")
    if not api_key:
        st.error("Manca la SERPER_API_KEY nei Secrets!")
        return []

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Query più ampia per non mancare i risultati
    payload = {
        "q": f"{query} azienda sede legale P.IVA",
        "gl": "it", 
        "hl": "it",
        "num": 8
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        
        companies = []
        for res in results:
            # Puliamo il titolo per identificare meglio l'azienda e la città
            title = res.get('title', '')
            snippet = res.get('snippet', '')
            
            # Aggiungiamo solo se sembra un risultato aziendale pertinente
            companies.append({
                "name": title.split(' - ')[0].split(' | ')[0],
                "location": snippet,
                "link": res.get('link')
            })
        return companies
    except Exception as e:
        st.error(f"Errore tecnico Serper: {e}")
        return []
