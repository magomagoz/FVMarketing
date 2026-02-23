import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query specifica per dati fiscali e geografici
    payload = {
        "q": f"{query} sede legale fatturato sito:reportaziende.it OR sito:ufficiocamerale.it OR sito:paginegialle.it",
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
                # 1. Fatturato
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                revenue = rev_match.group(0) if rev_match else "Dato non disp."

                # 2. SEDE LEGALE (Migliorata): Cerca il pattern "Città (Provincia)" o CAP
                loc_match = re.search(r'\b(?:sede|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', snippet)
                if not loc_match:
                    # Prova a cercare un CAP seguito da città
                    loc_match = re.search(r'\b\d{5}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', snippet)
                
                location = loc_match.group(1) if loc_match else "Verificare su sito"

                companies.append({
                    "name": title.split(' - ')[0].split(' | ')[0].split(',')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": location,
                    "revenue": revenue
                })
        return companies
    except:
        return []

def find_emails(company_name, person_name=""):
    """Cerca email istituzionali o personali sul web"""
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query per email istituzionale e specifica del referente
    query = f"email @{company_name.replace(' ', '').lower()}.it OR email @{company_name.replace(' ', '').lower()}.com"
    if person_name:
        query += f" OR \"{person_name}\" email"

    try:
        payload = {"q": query, "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        
        emails = []
        for r in res:
            found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.get('snippet', ''))
            emails.extend(found)
        
        # Pulizia: rimuove duplicati e email comuni non utili
        valid_emails = list(set([e.lower() for e in emails if not any(x in e for x in ['sentry', 'example', 'wix'])]))
        return valid_emails if valid_emails else ["info@" + company_name.replace(" ", "").lower() + ".it"]
    except:
        return ["Email non trovata"]

def search_decision_maker(company_name):
    # Funzione esistente potenziata con ricerca email per ogni lead
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    keyword = company_name.split()[0]
    
    try:
        payload = {"q": f"site:linkedin.com/in/ \"{keyword}\" (Responsabile OR Direttore)", "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        for r in res[:3]:
            nome = r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip()
            if len(nome.split()) < 5:
                # Per ogni lead trovato, proviamo a cercare la sua email
                leads.append({
                    "name": nome, 
                    "source": "LinkedIn",
                    "emails": find_emails(company_name, nome)
                })
        
        if not leads:
            leads = [{"name": "Direttore Generale", "source": "Ufficio Direzione", "emails": find_emails(company_name)}]
        return leads
    except:
        return [{"name": "Direttore Generale", "source": "Generico", "emails": ["Email non trovata"]}]
