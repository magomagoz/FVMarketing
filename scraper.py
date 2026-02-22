import requests
import streamlit as st
import re

def search_company_list(query):
    """Cerca solo aziende reali con Partita IVA."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query ristretta ai database aziendali per evitare siti di news o blog
    payload = {
        "q": f"{query} Partita IVA (sito:ufficiocamerale.it OR sito:reportaziende.it OR sito:paginegialle.it)",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snippet = res.get('snippet', '')
            title = res.get('title', '')
            
            # Estrazione P.IVA (11 cifre consecutive)
            piva_match = re.search(r'\b\d{11}\b', snippet + title)
            
            if piva_match:
                piva = piva_match.group(0)
                # Pulizia nome azienda da prefissi inutili
                clean_name = title.split(' - ')[0].split(' | ')[0].replace("Dati della società", "").strip()
                
                companies.append({
                    "name": clean_name,
                    "location": snippet[:60] + "...",
                    "piva": piva,
                    "revenue": re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE).group(0) if re.search(r'([\d.,]+\s?(mln|euro|€))', snippet, re.IGNORECASE) else "Non pubblico",
                    "link": res.get('link')
                })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    """Cerca referenti umani escludendo aziende e documenti."""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query focalizzata su profili personali LinkedIn e nomi propri
    query = f"site:linkedin.com/in/ \"{company_name}\" (Titolare OR Amministratore OR Direttore OR Owner)"
    
    try:
        payload = {"q": query, "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        
        # Parole che indicano che il risultato NON è una persona
        blacklist = ["srl", "spa", "p.iva", "partita iva", "pdf", "ordina", "recensioni", company_name.lower()]
        
        for r in res:
            name_candidate = r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip()
            
            # Validazione: il nome non deve contenere termini della blacklist e non deve essere troppo lungo
            if not any(word in name_candidate.lower() for word in blacklist) and len(name_candidate.split()) < 5:
                leads.append({
                    "name": name_candidate,
                    "source": "LinkedIn",
                    "link": r['link']
                })
        
        # Se non trova nessuno di specifico, restituisce un placeholder generico anziché dati sporchi
        return leads if leads else [{"name": "Direttore Generale", "source": "Ufficio Direzione"}]
    except:
        return [{"name": "Direttore Generale", "source": "Generico"}]
