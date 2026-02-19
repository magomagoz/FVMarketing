import time
import random
from validator import validate_piva_vies
from database import init_db, save_company, save_lead
from scraper import search_decision_maker, get_verified_email
from mailer import Mailer

# CONFIGURAZIONE (Usa variabili d'ambiente in produzione!)
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 465,
    'user': 'tua_mail@gmail.com',
    'pass': 'tua_password_app'
}

def process_company(company_name, piva):
    print(f"\n--- Elaborazione: {company_name} ---")
    
    # 1. Validazione Formale (VIES)
    info_ufficiale = validate_piva_vies(piva)
    if not info_ufficiale or not info_ufficiale['valid']:
        print(f"⚠️ Salto {company_name}: P.IVA non valida.")
        return

    # 2. Salvataggio Anagrafica nel Database
    save_company(piva, info_ufficiale['name'], info_ufficiale['address'])
    
    # 3. Ricerca Decision Maker (Scraping)
    print(f"🔍 Ricerca DG per {info_ufficiale['name']}...")
    lead_found = search_decision_maker(info_ufficiale['name'])
    
    if lead_found:
        # 4. Arricchimento Email (Hunter.io o simili)
        # Supponiamo di dedurre il dominio dal nome azienda o cercarlo
        dominio = f"{company_name.lower().replace(' ', '')}.it" 
        email = get_verified_email(lead_found['name'], dominio)
        
        if email:
            # 5. Salvataggio Lead e Invio Mail
            if save_lead(piva, lead_found['name'], email):
                print(f"📧 Invio mail a {lead_found['name']} ({email})...")
                
                mailer = Mailer(**SMTP_CONFIG)
                corpo_html = mailer.generate_body('email_dg.html', {
                    'lead_name': lead_found['name'],
                    'company_name': info_ufficiale['name'],
                    'city': info_ufficiale['address'].split(",")[-2].strip() if ',' in info_ufficiale['address'] else "Vostra sede",
                    'industry': "Innovazione" # Questo potrebbe essere dinamico
                })
                
                successo = mailer.send_mail(email, f"Domanda rapida per {lead_found['name']}", corpo_html)
                
                if successo:
                    print(f"✅ Processo completato per {company_name}")
            else:
                print(f"⏭️ Lead già presente nel DB, salto l'invio.")
        else:
            print(f"❌ Email non trovata per {lead_found['name']}")
    else:
        print(f"❌ Nessun DG trovato per {company_name}")

if __name__ == "__main__":
    # Inizializza il database al primo avvio
    init_db()
    
    # Esempio di lista aziende da processare
    aziende_target = [
        {"nome": "Eni S.p.A.", "piva": "00742640154"},
        # Aggiungi altre aziende qui...
    ]
    
    for azienda in aziende_target:
        process_company(azienda['nome'], azienda['piva'])
        
        # Pausa strategica anti-spam / anti-ban
        attesa = random.randint(30, 90)
        print(f"⏳ Attesa di {attesa} secondi prima della prossima azienda...")
        time.sleep(attesa)
