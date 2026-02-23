import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    payload = {
        "q": f"{query} sede legale città fatturato sito:reportaziende.it OR sito:paginegialle.it",
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
                
                # ESTRAZIONE CITTÀ: Cerchiamo pattern specifici di indirizzi italiani
                # Cerca CAP + Città + (PR)
                citta_match = re.search(r'\d{5}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', full_text)
                if not citta_match:
                    # Alternativa: Nome città seguito da (PR)
                    citta_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', full_text)
                
                citta = citta_match.group(1) if citta_match else "Non rilevata"

                companies.append({
                    "name": title.split(' - ')[0].split('|')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": citta,
                    "revenue": rev_match.group(0) if rev_match else "Dato non disp."
                })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query combinata per LinkedIn e Facebook
    query = f"(site:linkedin.com/in/ OR site:facebook.com) \"{company_name}\" (Titolare OR Responsabile OR Direttore)"
    
    try:
        payload = {"q": query, "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        
        for r in res[:5]:
            title = r.get('title', '')
            source = "LinkedIn" if "linkedin" in r.get('link', '') else "Facebook"
            
            # Pulizia nome
            nome = title.split(' - ')[0].split('|')[0].replace("Profilo ", "").replace(" | Facebook", "").strip()
            
            if len(nome.split()) < 5:
                # Fallback email se non trovata: genera info@...
                domain = company_name.replace(" ", "").lower()
                leads.append({
                    "name": nome,
                    "source": source,
                    "emails": [f"info@{domain}.it", f"amministrazione@{domain}.it"] 
                })
        
        return leads if leads else [{"name": "Direttore Generale", "source": "Generico", "emails": [f"info@{company_name.replace(' ','').lower()}.it"]}]
    except:
        return []
