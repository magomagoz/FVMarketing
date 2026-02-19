import requests
import streamlit as st

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

def get_verified_email(full_name, company_name):
    """
    Tenta di recuperare l'email (placeholder logica Hunter.io o deduzione).
    """
    # Per ora simuliamo una email basata sul dominio per testare il mailer
    dominio = f"{company_name.lower().replace(' ', '')}.it"
    nome_email = full_name.lower().replace(' ', '.')
    return f"{nome_email}@{dominio}"
