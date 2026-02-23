import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query specifica per Report Aziende e Ufficio Camerale
    payload = {
        "q": f"{query} fatturato sede legale sito:reportaziende.it OR sito:ufficiocamerale.it",
        "gl": "it", "hl": "it"
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        companies = []
        
        for res in results:
            title = res.get('title', '')
            snippet = res.get('snippet', '')
            full_text = (title + " " + snippet).lower()

            # 1. Partita IVA
            piva_match = re.search(r'\b\d{11}\b', full_text)
            if piva_match:
                piva = piva_match.group(0)
                
                # 2. Fatturato (cerca cifre seguite da mln o milioni)
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                revenue = rev_match.group(0) if rev_match else "Dato non disp."

                # 3. Sede Legale (estrae Città e Provincia)
                # Cerca pattern come "Roma (RM)" o "Milano" dopo parole chiave
                loc_match = re.search(r'(?:sede legale|sede):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\)|[A-Z][a-z]+)', snippet)
                if loc_match:
                    location = loc_match.group(1)
                else:
                    # Fallback: prende la località dal titolo se separata da virgola
                    location = title.split(',')[-1].split('-')[-1].strip() if ',' in title or '-' in title else "Italia"

                # 4. Pulizia Nome Azienda
                raw_name = title.split(' - ')[0].split(' | ')[0].split(',')[0]
                clean_name = re.sub(r'(?i)(s\.r\.l\.|srl|s\.p\.a\.|spa|partita iva.*)', '', raw_name).strip()
                
                companies.append({
                    "name": clean_name.upper(),
                    "piva": piva,
                    "location": location,
                    "revenue": revenue
                })
        return companies
    except Exception:
        return []

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Usa solo la prima parola per trovare referenti su LinkedIn
    keyword = company_name.split()[0]
    payload = {
        "q": f"site:linkedin.com/in/ \"{keyword}\" (Responsabile OR Direttore OR Owner)",
        "gl": "it", "hl": "it"
    }
    
    try:
        res = requests.post(search_url, json=payload, headers=headers).json().get('organic', [])
        leads = []
        for r in res:
            nome = r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip()
            if len(nome.split()) < 5 and not any(x in nome.lower() for x in ["srl", "spa", "p.iva"]):
                leads.append({"name": nome, "source": "LinkedIn", "link": r['link']})
        return leads if leads else [{"name": "Direttore Generale", "source": "Ufficio Direzione"}]
    except Exception:
        return [{"name": "Direttore Generale", "source": "Generico"}]
