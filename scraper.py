import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query mirata solo a siti che contengono dati aziendali certi
    payload = {
        "q": f"{query} P.IVA sede legale sito:ufficiocamerale.it OR sito:reportaziende.it OR sito:paginegialle.it",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snippet = res.get('snippet', '')
            title = res.get('title', '')
            
            # FILTRO 1: Cerca la P.IVA (11 cifre)
            piva_match = re.search(r'\b\d{11}\b', snippet + title)
            
            # FILTRO 2: Salta i risultati che parlano di "Bilancio", "Fatturato" come titoli
            blacklist = ["bilancio", "fatturato", "visura", "quotazione", "pdf"]
            if any(word in title.lower() for word in blacklist) and not piva_match:
                continue
                
            if piva_match:
                companies.append({
                    "name": title.split(' - ')[0].split(' | ')[0].replace("Dati della società", "").strip(),
                    "location": snippet[:60] + "...",
                    "piva": piva_match.group(0),
                    "revenue": re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE).group(0) if re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE) else "Non pubblico",
                    "link": res.get('link')
                })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query specifica per PERSONE, escludendo recensioni e PDF
    query = f"\"{company_name}\" (Titolare OR Amministratore OR CEO OR Direttore) -filetype:pdf -sito:paginegialle.it"
    
    try:
        payload = {"q": query, "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        for r in res:
            title = r['title']
            # FILTRO: Deve sembrare un nome di persona o un ruolo (esclude titoli lunghi o strani)
            if len(title.split()) < 10 and not any(x in title.lower() for x in ["ordine", "recensioni", "periodico"]):
                leads.append({
                    "name": title.split(' - ')[0].split(' | ')[0].strip(),
                    "source": "Web/Social",
                    "link": r['link']
                })
        
        return leads if leads else [{"name": "Direttore Generale", "source": "Generico"}]
    except:
        return [{"name": "Direttore Generale", "source": "Generico"}]
