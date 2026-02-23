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
            full_text = f"{title} {snippet}"
            piva_match = re.search(r'\b\d{11}\b', full_text)
            
            if piva_match:
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                
                # CITTÀ: Filtro rigoroso per escludere P.IVA e troncatura "Legale..."
                citta_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', full_text)
                if not citta_match:
                    citta_match = re.search(r'(?:sede|sita|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', full_text, re.IGNORECASE)
                
                citta_raw = citta_match.group(1).strip() if citta_match else "Da verificare"
                # Pulizia finale per evitare i bug visti negli screenshot
                if any(char.isdigit() for char in citta_raw) or "Legale" in citta_raw:
                    citta_pulita = "Verifica Sede"
                else:
                    citta_pulita = citta_raw

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
    
    # Query per scavare nelle prime 5 pagine
    query = f"(site:linkedin.com/in/ OR site:facebook.com) \"{company_name}\" (Amministratore OR Titolare OR CEO OR Direttore OR Owner)"
    
    try:
        # Usiamo 'num': 50 per coprire le prime 5 pagine in un colpo solo
        payload = {"q": query, "gl": "it", "hl": "it", "num": 50}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        domain = company_name.split()[0].lower().replace(",", "")
        
        for r in res:
            title = r.get('title', '')
            # Pulizia nome
            nome = title.split(' - ')[0].split('|')[0].replace("Profilo ", "").replace("LinkedIn", "").strip()
            
            if 1 < len(nome.split()) < 4:
                # Priorità ai ruoli decisionali (Rank 1)
                rank = 1 if any(x in title.lower() for x in ["amm", "titolare", "ceo", "owner", "proprietario"]) else 2
                
                if not any(l['name'] == nome for l in leads):
                    leads.append({
                        "name": nome,
                        "rank": rank,
                        "source": "LinkedIn" if "linkedin" in r.get('link','') else "Facebook",
                        "emails": [f"info@{domain}.it", f"direzione@{domain}.it", "e.magostini@sunecopower.it"]
                    })
        
        leads.sort(key=lambda x: x['rank'])
        return leads if leads else [{"name": "Direttore Generale", "rank": 3, "source": "Ufficio Direzione", "emails": [f"info@{domain}.it"]}]
    except: return []
