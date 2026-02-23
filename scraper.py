import requests
import streamlit as st
import re

def search_company_list(query):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    payload = {
        "q": f"{query} sede legale fatturato sito:reportaziende.it OR sito:ufficiocamerale.it",
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
                # FATTURATO
                rev_match = re.search(r'([\d.,]+\s?(mln|milioni|euro|€))', snippet, re.IGNORECASE)
                revenue = rev_match.group(0) if rev_match else "Dato non disp."

                # LOCALITÀ (Logica potenziata)
                # 1. Cerca Città (PROVINCIA)
                loc_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([A-Z]{2}\))', full_text)
                if loc_match:
                    location = loc_match.group(1)
                else:
                    # 2. Se non lo trova, prova a isolare la parte dopo l'ultimo trattino nel titolo
                    location = title.split('-')[-1].strip() if '-' in title else "Italia (Verificare)"

                companies.append({
                    "name": title.split(' - ')[0].split(' | ')[0].split(',')[0].strip().upper(),
                    "piva": piva_match.group(0),
                    "location": location,
                    "revenue": revenue
                })
        return companies
    except:
        return []

def find_emails(company_name, person_name=""):
    # Cerca email reali e genera quella istituzionale come fallback
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    domain = company_name.replace(" ", "").lower()
    query = f"email @{domain}.it OR email @{domain}.com"
    try:
        res = requests.post(search_url, json={"q": query}, headers={'X-API-KEY': api_key}).json().get('organic', [])
        emails = []
        for r in res:
            found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.get('snippet', ''))
            emails.extend(found)
        base_email = f"info@{domain}.it"
        valid = list(set([e.lower() for e in emails if domain in e.lower()]))
        return valid if valid else [base_email]
    except: return [f"info@{domain}.it"]

def search_decision_maker(company_name):
    search_url = "https://google.serper.dev/search"
    api_key = st.secrets.get("SERPER_API_KEY")
    keyword = company_name.split()[0]
    try:
        res = requests.post(search_url, json={"q": f"site:linkedin.com/in/ \"{keyword}\""}, headers={'X-API-KEY': api_key}).json().get('organic', [])
        leads = []
        for r in res[:3]:
            nome = r['title'].split(' - ')[0].split(' | ')[0].replace("Profilo ", "").strip()
            leads.append({"name": nome, "source": "LinkedIn", "emails": find_emails(company_name, nome)})
        return leads if leads else [{"name": "Direttore Generale", "source": "Generico", "emails": find_emails(company_name)}]
    except: return [{"name": "Direttore Generale", "source": "Generico", "emails": [f"info@{company_name.replace(' ','').lower()}.it"]}]
