import streamlit as st
import time
from validator import validate_piva_vies
from database import init_db, save_company
from scraper import search_decision_maker
from mailer import Mailer

st.set_page_config(page_title="Lead Gen Simulator", page_icon="🚀")

st.title("🛡️ Test Simulazione Lead Generation")
st.write("Questo test verificherà il flusso completo **senza inviare email**.")

# Inizializza DB
init_db()

# Input utente
target_name = st.text_input("Nome Azienda", "Eni S.p.A.")
target_piva = st.text_input("Partita IVA", "00742640154")

if st.button("Avvia Test Flusso"):
    with st.status("Esecuzione flusso in corso...", expanded=True) as status:
        
        # 1. VALIDAZIONE
        st.write("🔍 Controllo VIES...")
        info = validate_piva_vies(target_piva)
        if info and info['valid']:
            st.success(f"Azienda trovata: {info['name']}")
            save_company(target_piva, info['name'], info['address'])
        else:
            st.error("P.IVA non valida.")
            st.stop()

        # 2. SCRAPING
        st.write("🕵️ Ricerca Direttore Generale...")
        # Simuliamo un risultato per il test se non hai ancora le API keys
        lead = {"name": "Mario Rossi", "link": "https://linkedin.com/in/test"} 
        st.info(f"Lead individuato: {lead['name']}")

        # 3. GENERAZIONE EMAIL (DRY RUN)
        st.write("📝 Generazione template HTML...")
        mailer = Mailer("smtp.test.com", 465, "test@test.it", "password")
        
        dati_per_mail = {
            'lead_name': lead['name'],
            'company_name': info['name'],
            'city': info['address'].split(",")[0],
            'industry': "Innovazione Energetica"
        }
        
        try:
            corpo_html = mailer.generate_body('email_dg.html', dati_per_mail)
            st.write("✅ Anteprima Email generata con successo.")
            
            with st.expander("Visualizza Anteprima Mail"):
                st.components.v1.html(corpo_html, height=400, scrolling=True)
                
            st.warning("🚫 MODO TEST: Invio email saltato intenzionalmente.")
        except Exception as e:
            st.error(f"Errore nel template: {e}")

        status.update(label="Test Completato!", state="complete", expanded=False)

st.divider()
st.caption("iPad Pro Project - Marketing Automation v1.0")
