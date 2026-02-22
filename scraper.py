import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query specifica per trovare dati fiscali e geografici
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
            # Cerchiamo la P.IVA nel testo (11 cifre)
            piva_match = re.search(r'\b\d{11}\b', snippet)
            piva = piva_match.group(0) if piva_match else "Non trovata"
            
            # Cerchiamo di intercettare il fatturato (es: "fatturato di 10 mln")
            fatturato_match = re.search(r'(fatturato|ricavi)[:\s]+([\d.,]+\s?(mln|mila|euro|€))', snippet, re.IGNORECASE)
            fatturato = fatturato_match.group(2) if fatturato_match else "Dato non pubblico"

            companies.append({
                "name": res.get('title', '').split(' - ')[0].split(' | ')[0],
                "location": snippet[:120] + "...",
                "piva": piva,
                "revenue": fatturato,
                "link": res.get('link')
            })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    """Cerca attivamente profili LinkedIn e Social."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Cerchiamo specificamente su LinkedIn e pagine "Chi Siamo"
    payload = {
        "q": f"site:linkedin.com/in/ \"{company_name}\" (titolare OR direttore OR CEO OR owner)",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        leads = []
        for res in results:
            leads.append({
                "name": res.get('title', '').split(' - ')[0].split(' | ')[0],
                "source": "LinkedIn",
                "link": res.get('link'),
                "snippet": res.get('snippet')
            })
        # Se non trova nessuno su LinkedIn, aggiungiamo un placeholder generico
        if not leads:
            leads.append({"name": "Direttore Generale", "source": "Ricerca Generica", "link": "#", "snippet": "Nessun profilo social diretto trovato."})
        return leads
    except:
        return [{"name": "Direttore Generale", "source": "Errore ricerca", "link": "#", "snippet": ""}]
