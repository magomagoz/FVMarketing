import streamlit as st
import time
from validator import validate_piva_vies
from scraper import search_decision_maker, get_verified_email
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

# --- MAIN ---
if st.session_state.get('data_found'):
    df = st.session_state.data_found
    
    with st.container(border=True):
        st.subheader(f"📊 {df['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", df['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", df['corp']['revenue'])
        with c3: st.metric("📍 Sede Legale", df['corp']['location'])

    st.subheader("👥 Referente per la e-mail")
    lead_idx = [l['name'] for l in df['leads']].index(st.selectbox("🎯 Destinatario:", [l['name'] for l in df['leads']]))
    lead_scelto = df['leads'][lead_idx]
    nome_gentile = lead_scelto['name'].split()[0] if lead_scelto['name'] != "Direttore Generale" else "Direttore"

    # 1. DEFINIAMO IL TESTO PRIMA DI USARLO
    testo_pieno = f"""Gentile {nome_gentile},

Le scrivo perché ora l'impianto fotovoltaico per la sua Azienda potrà beneficiare dell'IperAmmortamento 2026, che le permetterà di recuperare il 67% del suo investimento in Credito d'Imposta, immediatamente esigibile già dal 2027.

In allegato troverà una simulazione di impianto fotovoltaico con il ROI che le agevolazioni permettono: potrà vedere come l'investimento si ripaga immediatamente, grazie al risparmio energetico e all'IperAmmortamento 2026.

Vorrei avere l'opportunità di analizzare i suoi consumi per proporle, senza nessun impegno, il corretto Ritorno sull'Investimento.

Non esiti nel contattarmi per ogni delucidazione in merito.

Un cordiale saluto.

Enrico Magostini
Consulente Energetico

SUN ECO POWER S.r.l.
Mobile: +39 334 607 9956
e-mail: e.magostini@sunecopower.it
P.IVA/C.F: 01870010855
REA: CL-104471

www.sunecopower.it

Le informazioni contenute nella presente comunicazione e i relativi allegati possono essere riservate e sono, comunque, destinate esclusivamente alle persone o alla Società sopraindicati."""

    # Inizializza la bozza se non esiste
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = testo_pieno

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
