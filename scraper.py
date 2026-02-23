import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query più ampia per beccare la sede legale subito
    payload = {
        "q": f"{query} sede legale città fatturato sito:reportaziende.it OR sito:ufficiocamerale.it OR sito:paginegialle.it",
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
                # ESTRAZIONE CITTÀ (Migliorata)
                # Cerca pattern: "Comune (PR)", "CAP Comune", "Sede a Comune"
                citta_match = re.search(r'(?:sede|base|in)\s+(?:a|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', full_text, re.IGNORECASE)
                if not citta_match:
                    citta_match = re.search(r'\b\d{5}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', full_text)
                
                citta = citta_match.group(1) if citta_match else "Da verificare"

                companies.append({
                    "name": title.split(' - ')[0].split('|')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": citta.split('(')[0].strip(), # Puliamo eventuali parentesi
                    "revenue": re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE).group(0) if re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE) else "Dato non disp."
                })
        return companies
    except: return []

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query mirata per trovare Monica Diaz e i vertici (LinkedIn + Facebook)
    queries = [
        f"site:linkedin.com/in/ \"{company_name}\" (Titolare OR Amministratore OR Monica Diaz)",
        f"site:facebook.com \"{company_name}\" (Titolare OR Proprietario)"
    ]
    
    leads = []
    for q in queries:
        try:
            res = requests.post(search_url, json={"q": q, "gl": "it", "hl": "it"}, headers=headers).json().get('organic', [])
            for r in res:
                nome = r.get('title', '').split(' - ')[0].split('|')[0].replace("Profilo ", "").replace(" | Facebook", "").strip()
                if len(nome.split()) < 5 and not any(x['name'] == nome for x in leads):
                    domain = company_name.replace(" ", "").lower()
                    leads.append({
                        "name": nome,
                        "source": "LinkedIn" if "linkedin" in r.get('link', '') else "Facebook",
                        "emails": [f"info@{domain}.it", f"direzione@{domain}.it"]
                    })
        except: continue
    
    return leads if leads else [{"name": "Direttore Generale", "source": "Generico", "emails": [f"info@{company_name.replace(' ','').lower()}.it"]}]
