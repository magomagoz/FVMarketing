from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import requests
import zeep
from jinja2 import Template

def generate_personalized_email(piva_info, lead_info):
    # Carichiamo il template
    with open("template_email.html") as f:
        template = Template(f.read())
    
    # Mock dei dati estratti (qui andrebbe la logica dello scraper precedente)
    data = {
        "lead_name": lead_info['full_name'],
        "company_name": piva_info['name'],
        "industry": "Energia e Innovazione", # Dato che potresti estrarre dal sito
        "city": piva_info['address'].split(",")[-2].strip(), # Estraiamo la città dall'indirizzo VIES
        "pain_point": "gestione flussi digitali",
        "unsubscribe_link": "https://tua-agency.it/opt-out"
    }
    
    return template.render(data)

# Flusso:
# 1. Valido P.IVA -> 2. Cerco Lead su Web -> 3. Genero Email
piva_data = validate_piva_vies("00742640154")
if piva_data and piva_data['valid']:
    lead_data = {"full_name": "Mario Rossi"} # Risultato dello scraping
    email_finale = generate_personalized_email(piva_data, lead_data)
    print("Email Pronta per l'invio!")

def validate_piva_vies(vat_number, country_code='IT'):
    """
    Verifica se la Partita IVA è valida e attiva nel database VIES.
    """
    url = 'https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'
    client = zeep.Client(wsdl=url)
    
    try:
        result = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        if result.valid:
            print(f"✅ Azienda Trovata: {result.name}")
            return {
                "valid": True,
                "name": result.name,
                "address": result.address.replace("\n", ", ")
            }
        else:
            print("❌ Partita IVA non valida o cessata.")
            return {"valid": False}
    except Exception as e:
        print(f"⚠️ Errore durante la validazione: {e}")
        return None

# Esempio d'uso
# info_azienda = validate_piva_vies("00742640154") # P.IVA Eni S.p.A.

def search_decision_maker(company_name):
    # Eseguiamo una ricerca mirata su Google via API
    # Query: "Direttore Generale [Nome Azienda] LinkedIn"
    api_key = "TUO_SERPAPI_KEY"
    query = f"Direttore Generale {company_name} LinkedIn"
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }
    
    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json().get("organic_results", [])
    
    if results:
        # Il primo risultato solitamente è il profilo più rilevante
        top_result = results[0]
        return {
            "name": top_result.get("title").split("-")[0].strip(),
            "profile_url": top_result.get("link")
        }
    return None

def get_verified_email(full_name, domain):
    api_key = "TUA_HUNTER_API_KEY"
    first_name, last_name = full_name.split(" ")[0], full_name.split(" ")[1]
    
    url = f"https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first_name}&last_name={last_name}&api_key={api_key}"
    
    res = requests.get(url).json()
    if res['data'] and res['data']['verification']['status'] == 'deliverable':
        return res['data']['email']
    return None

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    vat_number = Column(String) # P.IVA da CCIAA
    website = Column(String)
    industry = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    company_id = Column(ForeignKey('companies.id'))
    full_name = Column(String)
    role = Column(String) # es. "Direttore Generale"
    email = Column(String, unique=True)
    phone = Column(String)
    status = Column(String, default='found') # found, contacted, bounced
    last_contacted = Column(DateTime)


