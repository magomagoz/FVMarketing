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
