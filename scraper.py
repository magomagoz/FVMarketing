import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query rinforzata per forzare Google a mostrare sede e fatturato negli snippet
    payload = {
        "q": f"{query} sede legale fatturato euro sito:reportaziende.it OR sito:ufficiocamerale.it",
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
                # ESTRAZIONE FATTURATO: Cerca pattern come "10.000.000", "5 mln", "euro 100.000"
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                revenue = rev_match.group(0) if rev_match else "Richiedi Visura"

                # ESTRAZIONE SEDE LEGALE: Cerca CAP + Città o nomi di città noti
                # Cerchiamo di isolare la parte che sembra un indirizzo
                loc_match = re.search(r'(?:sede a|basata a|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', snippet)
                if loc_match:
                    location = loc_match.group(1)
                else:
                    # Fallback: prendiamo l'ultima parola del titolo prima dei trattini
                    location = title.split('-')[0].split(',')[-1].strip()

                companies.append({
                    "name": title.split(' - ')[0].replace('S.r.l.', '').replace('Srl', '').strip().upper(),
                    "piva": piva_match.group(0),
                    "location": location,
                    "revenue": revenue
                })
        return companies
    except:
        return []

def search_decision_maker(company_name):
    # (Mantieni la funzione search_decision_maker che già funziona bene)
    # Assicurati solo che restituisca una lista di dizionari
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    keyword = company_name.split()[0]
    try:
        payload = {"q": f"site:linkedin.com/in/ \"{keyword}\" (Responsabile OR Direttore)", "gl": "it", "hl": "it"}
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = [{"name": r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip(), "source": "LinkedIn"} for r in res[:3]]
        return leads if leads else [{"name": "Direttore Generale", "source": "Ufficio Direzione"}]
    except:
        return [{"name": "Direttore Generale", "source": "Generico"}]
