import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    # Query mirata a Report Aziende e Ufficio Camerale per dati fiscali certi
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
            full_text = (title + " " + snippet).replace("...", "")

            # 1. Estrazione P.IVA (11 cifre)
            piva_match = re.search(r'\b\d{11}\b', full_text)
            if piva_match:
                piva = piva_match.group(0)
                
                # 2. Estrazione FATTURATO (Cerca cifre seguite da mln, €, euro)
                # Esempio: "10,5 mln", "500.000 €"
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                revenue = rev_match.group(0) if rev_match else "Dato non disp."

                # 3. Estrazione LOCALITÀ (Cerca CAP + Provincia o pattern indirizzo)
                # Cerchiamo pattern tipo "00100 Roma" o "Via ... , Milano"
                loc_match = re.search(r'(\d{5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', snippet)
                if loc_match:
                    location = loc_match.group(0)
                else:
                    # Fallback: prova a prendere la parte dopo la virgola nel titolo
                    location = title.split(',')[-1].strip() if ',' in title else "Italia"

                # 4. Pulizia Nome Azienda
                raw_name = title.split(' - ')[0].split(' | ')[0].split(',')[0]
                clean_name = re.sub(r'(?i)(s\.r\.l\.|srl|s\.p\.a\.|spa|partita iva.*)', '', raw_name).strip()
                
                companies.append({
                    "name": clean_name,
                    "piva": piva,
                    "location": location,
                    "revenue": revenue
                })
        return companies
    except Exception as e:
        return []
