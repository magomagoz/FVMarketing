import requests
import streamlit as st
import re

def search_company_list(query):
    """Cerca aziende e tenta di estrarre P.IVA e Fatturato dallo snippet."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    payload = {
        "q": f"{query} sede legale P.IVA fatturato sito:reportaziende.it OR sito:ufficiocamerale.it",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snippet = res.get('snippet', '')
            # Regex per P.IVA (11 cifre)
            piva_match = re.search(r'\b\d{11}\b', snippet)
            # Regex per Fatturato (cerca cifre seguite da mln o euro)
            fatt_match = re.search(r'(\d+[\.,]?\d*\s?(mln|mila|euro|€))', snippet, re.IGNORECASE)
            
            companies.append({
                "name": res.get('title', '').split(' - ')[0].split(' | ')[0],
                "location": snippet[:100],
                "piva": piva_match.group(0) if piva_match else "Da verificare",
                "revenue": fatt_match.group(0) if fatt_match else "Non pubblico",
                "link": res.get('link')
            })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    """Cerca i Decision Maker su LinkedIn."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    payload = {
        "q": f"site:linkedin.com/in/ \"{company_name}\" (titolare OR direttore OR CEO)",
        "gl": "it", "hl": "it"
    }
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        if not results:
            return [{"name": "Direttore Generale", "source": "Generico", "link": "#", "snippet": "Nessun profilo social trovato."}]
        return [{"name": r['title'].split(' - ')[0], "source": "LinkedIn", "link": r['link'], "snippet": r['snippet']} for r in results]
    except:
        return [{"name": "Direttore Generale", "source": "Generico", "link": "#", "snippet": ""}]
