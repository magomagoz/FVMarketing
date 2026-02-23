import requests
import streamlit as st
import re

# Chiavi API (da inserire in un file .env per sicurezza)
SERPER_API_KEY = "TUA_SERPER_API_KEY"
HUNTER_API_KEY = "TUA_HUNTER_API_KEY"

def search_decision_maker(company_name):
    """
    Cerca profili chiave su LinkedIn e Facebook via API Serper.
    """
    # Se non hai ancora configurato i Secrets, usiamo un fallback di test
    if "SERPER_API_KEY" not in st.secrets:
        return {"name": "Ricerca non configurata", "link": "#", "snippet": "Aggiungi SERPER_API_KEY nei Secrets"}

    url = "https://google.serper.dev/search"
    # Cerchiamo su più piattaforme social contemporaneamente
    query = f'site:linkedin.com/in/ OR site:facebook.com "{company_name}" (Direttore OR CEO OR Titolare)'
    
    payload = {"q": query, "num": 5}
    headers = {
        'X-API-KEY': st.secrets["SERPER_API_KEY"],
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        
        if results:
            # Prendiamo il primo risultato più rilevante
            res = results[0]
            return {
                "name": res.get('title', '').split('-')[0].split('|')[0].strip(),
                "link": res.get('link'),
                "snippet": res.get('snippet', ''),
                "source": "LinkedIn" if "linkedin" in res.get('link') else "Facebook"
            }
    except Exception as e:
        print(f"Errore scraping: {e}")
    
    return None

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
