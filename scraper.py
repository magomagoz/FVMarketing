import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    
    # FIX: Intestazione corretta
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query ristretta per P.IVA
    payload = {
        "q": f"{query} Partita IVA (sito:reportaziende.it OR sito:ufficiocamerale.it OR sito:paginegialle.it)",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"Errore API Serper: {response.text}") # Utile per il debug
            
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snippet = res.get('snippet', '')
            title = res.get('title', '')
            piva_match = re.search(r'\b\d{11}\b', snippet + title)
            
            if piva_match:
                companies.append({
                    "name": title.split(' - ')[0].split(' | ')[0].replace("Dati della società", "").strip(),
                    "piva": piva_match.group(0),
                    "location": snippet[:60] + "...",
                    "revenue": re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE).group(0) if re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE) else "Non pubblico",
                    "link": res.get('link')
                })
        return companies
    except Exception as e:
        print(f"Errore Scraping Aziende: {e}")
        return []

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    
    # FIX: Intestazione corretta
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query per trovare Monica e colleghi
    query = f"site:linkedin.com/in/ \"{company_name}\""
    
    try:
        payload = {"q": query, "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        blacklist = ["srl", "spa", "p.iva", "recensioni", company_name.lower()]
        
        for r in res:
            nome_candidato = r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip()
            if not any(b in nome_candidato.lower() for b in blacklist) and len(nome_candidato.split()) < 5:
                leads.append({
                    "name": nome_candidato,
                    "source": "LinkedIn",
                    "link": r['link']
                })
        
        return leads if leads else [{"name": "Direttore Generale", "source": "Ufficio Direzione"}]
    except Exception as e:
        print(f"Errore Scraping Leads: {e}")
        return [{"name": "Direttore Generale", "source": "Generico"}]
