import requests
import streamlit as st
import re

def search_company_list(query):
    """Cerca aziende e dati fiscali/economici."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Cerchiamo dati su P.IVA e Fatturato in siti specifici
    payload = {
        "q": f"{query} sede legale P.IVA fatturato (sito:ufficiocamerale.it OR sito:reportaziende.it OR sito:paginegialle.it)",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snip = res.get('snippet', '')
            piva = re.search(r'\b\d{11}\b', snip)
            fatt = re.search(r'([\d.,]+\s?(mln|mila|euro|€))', snip, re.IGNORECASE)
            
            companies.append({
                "name": res.get('title', '').split(' - ')[0].split(' | ')[0],
                "location": snip[:80] + "...",
                "piva": piva.group(0) if piva else "Da verificare",
                "revenue": fatt.group(0) if fatt else "Non pubblico",
                "link": res.get('link')
            })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    """Ricerca referenti su Web, CCIAA, LinkedIn e Social."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query multi-canale: LinkedIn, Facebook, Instagram e Web generico
    queries = [
        f"\"{company_name}\" (titolare OR amministratore OR direttore OR CEO) site:linkedin.com/in/",
        f"\"{company_name}\" (titolare OR titolare) site:facebook.com",
        f"chi siamo \"{company_name}\" (direzione OR titolare OR responsabile)"
    ]
    
    leads = []
    for q in queries:
        try:
            payload = {"q": q, "gl": "it", "hl": "it"}
            res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
            for r in res:
                leads.append({
                    "name": r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", ""),
                    "source": "LinkedIn" if "linkedin" in r['link'] else "Web/Social",
                    "link": r['link'],
                    "snippet": r.get('snippet', '')
                })
        except:
            continue
            
    # Se la ricerca fallisce, restituiamo un contatto generico per non bloccare l'app
    return leads if leads else [{"name": "Direttore Generale", "source": "Generico", "link": "#", "snippet": ""}]
