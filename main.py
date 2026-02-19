# main.py
from validator import validate_piva_vies
from scraper import search_decision_maker
from mailer import generate_personalized_email # Qui caricherai l'HTML

def avvia_ricerca(nome_azienda, piva):
    # STEP 1: Validazione Formale
    azienda_ufficiale = validate_piva_vies(piva)
    
    if azienda_ufficiale and azienda_ufficiale['valid']:
        
        # STEP 2: Scraping (Il Punto 2 che chiedevi)
        print(f"Cerco il Direttore Generale per {azienda_ufficiale['name']}...")
        lead = search_decision_maker(azienda_ufficiale['name'])
        
        if lead:
            # STEP 3: Preparazione Mail (Usa il template HTML)
            corpo_mail = generate_personalized_email(azienda_ufficiale, lead)
            
            # Qui potresti salvare tutto nel Database prima di inviare
            print("Processo completato. Lead pronta per l'invio!")
            return corpo_mail

# Esecuzione
avvia_ricerca("Eni S.p.A.", "00742640154")
