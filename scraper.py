import requests
import streamlit as st
import re

# Chiavi API (da inserire in un file .env per sicurezza)
SERPER_API_KEY = "TUA_SERPER_API_KEY"
HUNTER_API_KEY = "TUA_HUNTER_API_KEY"

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
                # 1. Fatturato
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                
                # 2. CITTÀ (Ricerca specifica per Comune e Provincia)
                # Cerca pattern: Pomezia (RM), Roma, Aprilia (LT)
                citta_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', full_text)
                if not citta_match:
                    citta_match = re.search(r'(?:sede|base|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', full_text)
                
                citta = citta_match.group(1) if citta_match else "Da verificare"

                companies.append({
                    "name": title.split(' - ')[0].split('|')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": citta.split(' - ')[0].strip(),
                    "revenue": rev_match.group(0) if rev_match else "Dato non disp."
                })
        return companies
    except: return []

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query specifica per trovare Monica Diaz e vertici aziendali
    query = f"(site:linkedin.com/in/ OR site:facebook.com) \"{company_name}\" (Monica Diaz OR Amministratore OR Titolare OR Owner)"
    
    try:
        res = requests.post(search_url, json={"q": query, "gl": "it", "hl": "it"}, headers=headers).json().get('organic', [])
        leads = []
        domain = company_name.split()[0].lower().replace(" ", "")
        
        for r in res[:6]:
            nome = r.get('title', '').split(' - ')[0].split('|')[0].replace("Profilo ", "").replace(" | Facebook", "").strip()
            if len(nome.split()) < 5:
                leads.append({
                    "name": nome,
                    "source": "LinkedIn" if "linkedin" in r.get('link', '') else "Facebook/Web",
                    "emails": [f"info@{domain}.it", f"direzione@{domain}.it", f"amministrazione@{domain}.it"]
                })
        return leads if leads else [{"name": "Direttore Generale", "source": "Ufficio Direzione", "emails": [f"info@{domain}.it"]}]
    except: return []

def get_verified_email(full_name, company_domain):
    """
    Trova e verifica l'email usando l'API di Hunter.io
    """
    # Pulizia nome per l'API
    parts = full_name.split()
    if len(parts) < 2:
        return None
    
    first_name = parts[0]
    last_name = parts[-1]
    
    url = f"https://api.hunter.io/v2/email-finder?domain={company_domain}&first_name={first_name}&last_name={last_name}&api_key={HUNTER_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json().get('data', {})
        
        if data and data.get('verification', {}).get('status') == 'deliverable':
            print(f"✅ Email verificata trovata: {data['email']}")
            return data['email']
        
        # Se non è "deliverable", meglio non rischiare il bounce
        return None
    except Exception as e:
        print(f"⚠️ Errore durante la ricerca email: {e}")
        return None

def extract_domain_from_url(url):
    """
    Utility per estrarre il dominio (es. azienda.it) da un URL
    """
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    return match.group(1) if match else None

def search_robust_people(company_name):
    """
    Ricerca avanzata su LinkedIn e Facebook tramite Serper/Google.
    """
    # Query per LinkedIn: cerca persone con ruoli chiave
    linkedin_query = f'site:linkedin.com/in/ "{company_name}" ("Direttore" OR "CEO" OR "Titolare")'
    
    # Query per Facebook: utile per PMI italiane dove il titolare è molto attivo
    facebook_query = f'site:facebook.com "{company_name}" (Titolare OR Proprietario)'
    
    results = []
    
    # Eseguiamo le chiamate (Esempio per LinkedIn)
    # Nota: Assicurati di avere la chiave SERPER_API_KEY nei segreti di Streamlit
    headers = {'X-API-KEY': st.secrets["SERPER_API_KEY"], 'Content-Type': 'application/json'}
    
    for q in [linkedin_query, facebook_query]:
        response = requests.post(
            "https://google.serper.dev/search", 
            json={"q": q, "num": 3}, 
            headers=headers
        )
        if response.status_code == 200:
            organic = response.json().get('organic', [])
            for res in organic:
                results.append({
                    "source": "LinkedIn" if "linkedin" in res['link'] else "Facebook",
                    "title": res['title'],
                    "link": res['link'],
                    "snippet": res.get('snippet', '')
                })
    
    return results
