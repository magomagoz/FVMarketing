import requests

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
