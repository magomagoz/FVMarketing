import requests
import streamlit as st

def search_decision_maker(company_name):
    """Cerca profili su LinkedIn/Facebook via Serper."""
    # Se non c'è la chiave, restituiamo un segnaposto per non far crashare l'app
    api_key = st.secrets.get("SERPER_API_KEY")
    if not api_key:
        return [{"name": "Configura Serper API", "link": "#", "source": "Info", "snippet": "Vedi istruzioni sotto"}]

    url = "https://google.serper.dev/search"
    query = f'site:linkedin.com/in/ OR site:facebook.com "{company_name}" (Direttore OR CEO OR Titolare)'
    
    try:
        response = requests.post(url, json={"q": query}, headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'})
        results = response.json().get('organic', [])
        return [{
            "name": res.get('title', '').split('-')[0].split('|')[0].strip(),
            "link": res.get('link'),
            "source": "LinkedIn" if "linkedin" in res.get('link') else "Facebook",
            "snippet": res.get('snippet', '')
        } for res in results]
    except:
        return []

def get_verified_email(full_name, company_name):
    """Simula il recupero email per il test."""
    dominio = f"{company_name.lower().replace(' ', '')}.it"
    return f"{full_name.lower().replace(' ', '.')}@{dominio}"
