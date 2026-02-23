import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    payload = {
        "q": f"{query} sede legale città fatturato sito:reportaziende.it OR sito:ufficiocamerale.it",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        for res in results:
            snippet = res.get('snippet', '')
            title = res.get('title', '')
            piva_match = re.search(r'\b\d{11}\b', f"{title} {snippet}")
            if piva_match:
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                # Estrazione città pulita
                citta_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', snippet)
                citta = citta_match.group(1) if citta_match else "Da verificare"
                
                companies.append({
                    "name": title.split(' - ')[0].split('|')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": citta,
                    "revenue": rev_match.group(0) if rev_match else "Dato non disp."
                })
        return companies
    except: return []

def search_linkedin_leads(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query profonda su LinkedIn per trovare Amministratori e Titolari
    query = f"site:linkedin.com/in/ \"{company_name}\" (Amministratore OR Titolare OR CEO OR Owner OR Monica Diaz)"
    
    try:
        # num: 50 permette di scansionare le prime 5 pagine di risultati
        payload = {"q": query, "gl": "it", "hl": "it", "num": 50}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        domain = company_name.split()[0].lower().replace(",", "")
        
        for r in res:
            title = r.get('title', '')
            # Pulizia nome: estraiamo solo Nome e Cognome
            nome = title.split(' - ')[0].split('|')[0].replace("Profilo ", "").replace("LinkedIn", "").strip()
            
            if 1 < len(nome.split()) < 4:
                # Rank 1 per ruoli decisionali, Rank 2 per altri
                is_boss = any(x in title.lower() for x in ["amm", "titolare", "ceo", "owner", "monica"])
                leads.append({
                    "name": nome,
                    "rank": 1 if is_boss else 2,
                    "role": "Decision Maker" if is_boss else "Profilo LinkedIn",
                    "emails": [f"info@{domain}.it", f"direzione@{domain}.it", "e.magostini@sunecopower.it"]
                })
        
        # Ordiniamo per importanza
        leads.sort(key=lambda x: x['rank'])
        return leads if leads else [{"name": "Direttore Generale", "rank": 3, "role": "Ufficio Direzione", "emails": [f"info@{domain}.it"]}]
    except: return []
