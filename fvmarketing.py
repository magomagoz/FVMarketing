import streamlit as st
import time
from validator import validate_piva_vies
#from scraper import search_decision_maker, get_verified_email
from mailer import Mailer

# Configurazione Mailer (Mock per il test)
mailer = Mailer("smtp.gmail.com", 465, "test@test.it", "password")

st.title("🚀 Business Lead Finder")

# --- FASE 1: INPUT ---
with st.sidebar:
    st.header("Ricerca Azienda")
    company_input = st.text_input("Nome Azienda o P.IVA")
    search_button = st.button("Analizza Azienda")

# Inizializziamo lo stato della sessione per "ricordare" i dati tra un click e l'altro
if 'data_found' not in st.session_state:
    st.session_state.data_found = None

# --- FASE 2: ELABORAZIONE ---
if search_button and company_input:
    with st.spinner("Recupero informazioni in corso..."):
        # Se l'input è numerico, proviamo la validazione P.IVA
        if company_input.isdigit():
            info_corp = validate_piva_vies(company_input)
        else:
            # Qui potresti aggiungere una ricerca Google per trovare la P.IVA dal nome
            # Per ora usiamo il nome direttamente per lo scraping
            info_corp = {"name": company_input.title(), "address": "Indirizzo non trovato", "valid": True}

        if info_corp and info_corp.get('valid'):
            # Cerchiamo il Direttore Generale
            lead = search_decision_maker(info_corp['name'])
            
            # Salviamo tutto nello stato della sessione
            st.session_state.data_found = {
                "corp": info_corp,
                "lead": lead,
                "email": "mario.rossi@azienda.it" # Simulazione email trovata
            }
        else:
            st.error("Impossibile trovare dati validi per questa azienda.")

# --- FASE 3: VISUALIZZAZIONE E DECISIONE ---
if st.session_state.data_found:
    data = st.session_state.data_found
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Dati Aziendali")
        st.write(f"**Ragione Sociale:** {data['corp']['name']}")
        st.write(f"**Indirizzo:** {data['corp']['address']}")
    
    with col2:
        st.subheader("👤 Decision Maker")
        if data['lead']:
            st.write(f"**Nome:** {data['lead']['name']}")
            st.write(f"**Ruolo:** Direttore Generale")
            st.write(f"**Email:** {data['email']}")
        else:
            st.warning("Nessun contatto trovato.")

    st.divider()

    # Anteprima della Mail
    st.subheader("📧 Anteprima Comunicazione")
    corpo_mail = mailer.generate_body('email_dg.html', {
        'lead_name': data['lead']['name'] if data['lead'] else "Direttore",
        'company_name': data['corp']['name'],
        'city': "vostra sede",
        'industry': "Innovazione"
    })
    
    with st.container(border=True):
        st.components.v1.html(corpo_html, height=300, scrolling=True)

    # Bottoni decisionali
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Approva e Invia", use_container_width=True, type="primary"):
            st.success(f"Mail inviata con successo a {data['email']}!")
            # Qui andrebbe mailer.send_mail(...)
            st.session_state.data_found = None # Reset
    with c2:
        if st.button("❌ Scarta Lead", use_container_width=True):
            st.info("Lead scartato.")
            st.session_state.data_found = None # Reset
