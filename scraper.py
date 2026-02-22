import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Cerchiamo dati fiscali e geografici
    payload = {
        "q": f"{query} sede legale P.IVA fatturato",
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
                "piva": piva_match.group(0) if piva_match else "Verificare",
                "revenue": fatt_match.group(0) if fatt_match else "Dato non visibile",
                "link": res.get('link')
            })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    """Cerca attivamente su LinkedIn."""
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
        return [{"name": r['title'].split(' - ')[0], "source": "LinkedIn", "link": r['link'], "snippet": r['snippet']} for r in results] if results else []
    except:
        return []
