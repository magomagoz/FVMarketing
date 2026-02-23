import requests
import streamlit as st

def search_decision_maker(company_name):
    """
    Cerca profili chiave su LinkedIn e Facebook utilizzando query mirate.
    """
    if "SERPER_API_KEY" not in st.secrets:
        return {"name": "Configura API Key", "link": "#", "source": "Errore"}

    url = "https://google.serper.dev/search"
    # Cerchiamo specificamente profili personali su LinkedIn e pagine/post su Facebook
    queries = [
        f'site:linkedin.com/in/ "{company_name}" (Direttore OR CEO OR Titolare)',
        f'site:facebook.com "{company_name}" (Titolare OR Proprietario)'
    ]
    
    found_leads = []

    for q in queries:
        payload = {"q": q, "num": 3}
        headers = {'X-API-KEY': st.secrets["SERPER_API_KEY"], 'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=payload, headers=headers)
            results = response.json().get('organic', [])
            for res in results:
                found_leads.append({
                    "name": res.get('title', '').split('-')[0].split('|')[0].strip(),
                    "link": res.get('link'),
                    "snippet": res.get('snippet', ''),
                    "source": "LinkedIn" if "linkedin" in res.get('link') else "Facebook"
                })
        except Exception as e:
            st.error(f"Errore nella ricerca social: {e}")

    return found_leads # Restituiamo una lista di possibili candidati
