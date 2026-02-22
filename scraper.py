import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Cerchiamo solo su database aziendali affidabili
    payload = {
        "q": f"{query} Partita IVA sito:reportaziende.it OR sito:ufficiocamerale.it OR sito:paginegialle.it",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snippet = res.get('snippet', '')
            piva_match = re.search(r'\b\d{11}\b', snippet + res.get('title', ''))
            if piva_match:
                companies.append({
                    "name": res.get('title', '').split(' - ')[0].split(' | ')[0].strip(),
                    "piva": piva_match.group(0),
                    "location": snippet[:50] + "...",
                    "revenue": re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE).group(0) if re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE) else "Non pubblico"
                })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    """Ricerca mirata di persone su LinkedIn evitando rumore."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query specifica per trovare PERSONE associate all'azienda
    query = f"site:linkedin.com/in/ \"{company_name}\""
    
    try:
        payload = {"q": query, "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        
        # Blacklist per evitare che l'azienda appaia tra le persone
        blacklist = ["srl", "spa", "p.iva", "recensioni", company_name.lower()]
        
        for r in res:
            nome_candidato = r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip()
            
            # Filtro: Non deve essere l'azienda stessa e deve avere un nome breve (umano)
            if not any(b in nome_candidato.lower() for b in blacklist) and len(nome_candidato.split()) < 5:
                leads.append({
                    "name": nome_candidato,
                    "source": "LinkedIn",
                    "link": r['link']
                })
        
        # Se non trova nessuno, mette il placeholder ma non rompe l'app
        return leads if leads else [{"name": "Direttore Generale", "source": "Ufficio Direzione"}]
    except:
        return [{"name": "Direttore Generale", "source": "Generico"}]
