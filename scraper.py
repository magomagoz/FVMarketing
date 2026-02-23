import requests
import streamlit as st
import re

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query mirata: cerchiamo solo su LinkedIn profili con ruoli chiave
    # Usiamo num: 50 per coprire le prime 5 pagine di risultati
    query = f"site:linkedin.com/in/ \"{company_name}\" (Amministratore OR Titolare OR CEO OR Proprietario OR Owner OR Monica Diaz)"
    
    try:
        payload = {"q": query, "gl": "it", "hl": "it", "num": 50}
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        
        leads = []
        domain = company_name.split()[0].lower().replace(",", "")
        
        for res in results:
            title = res.get('title', '')
            # Pulizia: rimuove "Profilo", "LinkedIn" e tutto ciò che segue il nome
            # Esempio: "Monica Diaz - Amministratore Unico - Eurpack" -> "Monica Diaz"
            nome_pulito = title.split(' - ')[0].split('|')[0].replace("Profilo ", "").replace("LinkedIn", "").strip()
            
            # Validazione: Un nome professionale ha solitamente 2 o 3 parole
            if 1 < len(nome_pulito.split()) < 4:
                # Diamo priorità (rank 1) se nel titolo compaiono parole chiave decisionali
                is_top = any(x in title.lower() for x in ["amm", "titolare", "ceo", "owner", "proprietario"])
                rank = 1 if is_top else 2
                
                if not any(l['name'] == nome_pulito for l in leads):
                    leads.append({
                        "name": nome_pulito,
                        "rank": rank,
                        "role_info": "Top Management" if is_top else "Profilo Aziendale",
                        "link": res.get('link'),
                        "emails": [f"info@{domain}.it", f"direzione@{domain}.it", "e.magostini@sunecopower.it"]
                    })
        
        # Ordiniamo: Titolari e Amministratori per primi
        leads.sort(key=lambda x: x['rank'])
        
        # Se non trova nulla, restituisce un referente generico
        if not leads:
            leads = [{"name": "Direttore Generale", "rank": 3, "role_info": "Ufficio Direzione", "emails": [f"info@{domain}.it"]}]
            
        return leads
    except Exception as e:
        st.error(f"Errore ricerca LinkedIn: {e}")
        return []
