import requests
import streamlit as st
import re

def search_company_list(query):
    """Cerca l'azienda e pulisce il nome per le fasi successive"""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query ottimizzata per trovare dati ufficiali
    payload = {
        "q": f"{query} Partita IVA (sito:reportaziende.it OR sito:ufficiocamerale.it)",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        
        for res in results:
            title = res.get('title', '')
            snippet = res.get('snippet', '')
            
            # 1. Estrazione P.IVA
            piva_match = re.search(r'\b\d{11}\b', snippet + title)
            if piva_match:
                # 2. PULIZIA NOME: Rimuove tutto ciò che disturba la ricerca referenti
                # Toglie Srl, Spa, Partita IVA e caratteri speciali dal titolo
                raw_name = title.split(' - ')[0].split(' | ')[0].split(',')[0]
                clean_name = re.sub(r'(?i)(s\.r\.l\.|srl|s\.p\.a\.|spa|dati della società|partita iva.*)', '', raw_name).strip()
                
                companies.append({
                    "name": clean_name if clean_name else query.upper(),
                    "piva": piva_match.group(0),
                    "location": snippet[:60] + "...",
                    "revenue": "Non pubblico", # Espandibile con regex specifica
                    "link": res.get('link')
                })
        return companies
    except Exception as e:
        st.error(f"Errore ricerca aziende: {e}")
        return []

def search_decision_maker(company_name):
    """Cerca referenti su LinkedIn usando il nome pulito"""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Usiamo solo la prima parte del nome (es. "EURPACK") per massimizzare i risultati
    keyword = company_name.split()[0]
    query_linkedin = f"site:linkedin.com/in/ \"{keyword}\" (Responsabile OR Direttore OR Owner)"
    
    try:
        payload = {"q": query_linkedin, "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        
        # Parole da evitare nei nomi (per non prendere profili aziendali)
        blacklist = ["srl", "spa", "p.iva", "recensioni", "community", "pdf"]
        
        for r in res:
            nome_candidato = r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip()
            
            # Validazione: deve sembrare un nome umano (2-3 parole) e non essere in blacklist
            if not any(b in nome_candidato.lower() for b in blacklist) and 1 < len(nome_candidato.split()) < 5:
                leads.append({
                    "name": nome_candidato,
                    "source": "LinkedIn",
                    "link": r['link']
                })
        
        # Se trova Monica Diaz o altri, li restituisce. Altrimenti fallback su Direttore
        return leads if leads else [{"name": "Direttore Generale", "source": "Ufficio Direzione"}]
        
    except Exception as e:
        return [{"name": "Direttore Generale", "source": "Generico"}]
