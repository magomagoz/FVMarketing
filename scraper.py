import requests
import re

# Chiavi API (da inserire in un file .env per sicurezza)
SERPER_API_KEY = "TUA_SERPER_API_KEY"
HUNTER_API_KEY = "TUA_HUNTER_API_KEY"

def search_decision_maker(company_name):
    """
    Cerca il Direttore Generale su Google usando Serper.dev
    """
    url = "https://google.serper.dev/search"
    query = f'"{company_name}" (Direttore Generale OR "CEO" OR "General Manager") LinkedIn'
    
    payload = {"q": query}
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        results = response.json().get('organic', [])
        
        if results:
            # Analizziamo il primo risultato utile
            first_result = results[0]
            title = first_result.get('title', '')
            
            # Pulizia del nome: spesso il titolo è "Mario Rossi - Direttore Generale - Azienda"
            # Usiamo una regex semplice o split
            nome_estratto = title.split('-')[0].split('|')[0].strip()
            
            print(f"🎯 Trovato potenziale Lead: {nome_estratto}")
            return {
                "name": nome_estratto,
                "link": first_result.get('link')
            }
    except Exception as e:
        print(f"⚠️ Errore durante la ricerca Google: {e}")
    
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
