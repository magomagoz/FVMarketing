import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Setup
mailer = Mailer("smtp.gmail.com", 587, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])
st.set_page_config(layout="wide")
st.image("banner.png", use_container_width=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Ricerca Azienda")
    query = st.text_input("Inserisci Nome Azienda", key="input_query")
    
    if query:
        if 'companies' not in st.session_state or st.session_state.get('last_q') != query:
            st.session_state.companies = search_company_list(query)
            st.session_state.last_q = query

        if st.session_state.get('companies'):
            labels = [f"🏢 {c['name']} ({c['piva']})" for c in st.session_state.companies]
            idx = st.radio("Seleziona:", range(len(labels)), format_func=lambda x: labels[x])
            
            if st.button("🚀 ANALIZZA SELEZIONATA"):
                with st.spinner("Cercando referenti..."):
                    st.session_state.data_found = {
                        "corp": st.session_state.companies[idx],
                        "leads": search_decision_maker(st.session_state.companies[idx]['name'])
                    }
                    if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
                st.rerun()
        else:
            st.warning("Nessuna azienda trovata con P.IVA.")

    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 16px !important; white-space: normal !important; }
        [data-testid="stMetricLabel"] { font-size: 13px !important; }
        </style>
        """, unsafe_allow_html=True)

if st.session_state.get('data_found'):
    df = st.session_state.data_found
    
    with st.container(border=True):
        st.subheader(f"📊 {df['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", df['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", df['corp']['revenue'])
        with c3: st.metric("📍 Città", df['corp']['location']) # Rinominato in Città

    st.subheader("👥 Referenti individuati (LinkedIn, Facebook, Web)")
    nomi_leads = [f"{l['name']} ({l['source']})" for l in df['leads']]
    sel_lead_idx = nomi_leads.index(st.selectbox("🎯 Invia a questo contatto:", nomi_leads))
    lead_scelto = df['leads'][sel_lead_idx]
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
    
    # --- LISTA EMAIL APRIBILE ---
    with st.expander("📧 Email individuate (Seleziona)", expanded=False):
        email_selezionata = st.radio("Scegli indirizzo:", lead_scelto['emails'])
    
    # --- EDITOR (Inizialmente CHIUSO) ---
    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=False):
        # ... (Assicurati che qui ci sia la logica del testo_pieno definita prima)
        st.session_state.bozza_editor = st.text_area("Contenuto:", value=st.session_state.get('bozza_editor', ''), height=300)

    # --- ANTEPRIMA ---
    st.subheader("✍️ Anteprima")
    corpo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': corpo_html})
    st.components.v1.html(anteprima, height=400, scrolling=True)
    
    # --- CAMPO FINALE EDITABILE ---
    st.divider()
    destinatario_finale = st.text_input("📧 Destinatario finale (Editabile):", value=email_selezionata)

    if st.button("🚀 INVIA ORA", type="primary", use_container_width=True):
        if destinatario_finale:
            with st.spinner("Spedizione in corso..."):
                # ATTENZIONE: Usa i nomi corretti delle funzioni del tuo mailer.py
                corpo_html = st.session_state.bozza_editor.replace("\n", "<br>")
                anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': corpo_html})
                
                successo = mailer.send_mail(
                    receiver_email=destinatario_finale, 
                    subject=f"Proposta Fotovoltaico 2026 - {df['corp']['name']}",
                    body_html=anteprima
                )
                
                if successo:
                    st.balloons()
                    st.success(f"Mail inviata a {destinatario_finale}")
                else:
                    st.error("Errore nell'invio. Controlla le credenziali SMTP.")
