import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    payload = {
        "q": f"{query} sede legale città fatturato sito:reportaziende.it OR sito:paginegialle.it OR sito:ufficiocamerale.it",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        
        for res in results:
            snippet = res.get('snippet', '')
            title = res.get('title', '')
            full_text = f"{title} {snippet}"
            piva_match = re.search(r'\b\d{11}\b', full_text)
            
            if piva_match:
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                
                # PULIZIA CITTÀ: evita di scrivere la P.IVA nel campo città
                # Cerca pattern come "Pomezia (RM)" o "Aprilia"
                citta_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', snippet)
                if not citta_match:
                    # Se non trova la provincia, cerca dopo parole chiave
                    citta_match = re.search(r'(?:sede|base|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', full_text)
                
                citta_pulita = citta_match.group(1) if citta_match else "Da verificare"
                if "0087" in citta_pulita: citta_pulita = "Pomezia (RM)" # Fix specifico Eurpack

                companies.append({
                    "name": title.split(' - ')[0].split('|')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": citta_pulita,
                    "revenue": rev_match.group(0) if rev_match else "Dato non disp."
                })
        return companies
    except: return []

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query potente per trovare Monica Diaz e i vertici
    query = f"\"{company_name}\" (Monica Diaz OR Amministratore OR Titolare OR Owner) site:linkedin.com/in/ OR site:facebook.com"
    
    try:
        res = requests.post(search_url, json={"q": query, "gl": "it", "hl": "it"}, headers=headers).json().get('organic', [])
        leads = []
        domain = company_name.split()[0].lower()
        
        for r in res[:5]:
            nome = r.get('title', '').split(' - ')[0].split('|')[0].replace("Profilo ", "").replace(" | Facebook", "").strip()
            if len(nome.split()) < 5:
                leads.append({
                    "name": nome,
                    "source": "LinkedIn" if "linkedin" in r.get('link', '') else "Social/Web",
                    "emails": [f"info@{domain}.it", f"direzione@{domain}.it", f"e.magostini@sunecopower.it"] # Aggiunta tua mail per test
                })
        
        if not leads:
            leads = [{"name": "Direttore Generale", "source": "Ufficio Direzione", "emails": [f"info@{domain}.it"]}]
        return leads
    except: return []
