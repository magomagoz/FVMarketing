import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Configurazione Mailer
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])

st.set_page_config(layout="wide", page_title="FV Marketing Pro")
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
            labels = [f"🏢 {c['name']}" for c in st.session_state.companies]
            idx = st.radio("Seleziona:", range(len(labels)), format_func=lambda x: labels[x])
            if st.button("🚀 ANALIZZA SELEZIONATA"):
                st.session_state.data_found = {
                    "corp": st.session_state.companies[idx],
                    "leads": search_decision_maker(st.session_state.companies[idx]['name'])
                }
                if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
                st.rerun()

# --- MAIN ---
if st.session_state.get('data_found'):
    df = st.session_state.data_found
    
    with st.container(border=True):
        st.subheader(f"📊 {df['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", df['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", df['corp']['revenue'])
        with c3: st.metric("📍 Città", df['corp']['location'])

    st.subheader("👥 Referenti Individuati (Priorità Titolari)")
    nomi_leads = [f"{l['name']} [{l['source']}]" for l in df['leads']]
    
    # Fix NameError: Definiamo subito lead_scelto
    sel_box = st.selectbox("🎯 Seleziona destinatario:", nomi_leads)
    lead_scelto = df['leads'][nomi_leads.index(sel_box)]
    
    nome_gentile = lead_scelto['name'].split()[0] if "Direttore" not in lead_scelto['name'] else "Direttore"

    with st.expander("📧 VEDI EMAIL TROVATE", expanded=False):
        email_sel = st.radio("Invia a:", lead_scelto['emails'])
    
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

    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = testo_base

    with st.expander("📝 MODIFICA TESTO", expanded=False):
        st.session_state.bozza_editor = st.text_area("Corpo:", value=st.session_state.bozza_editor, height=250)

    # Anteprima HTML
    corpo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': corpo_html})
    st.subheader("✍️ Anteprima")
    st.components.v1.html(anteprima, height=300, scrolling=True)

    if st.button("🚀 INVIA ORA", type="primary", use_container_width=True):
        if mailer.send_mail(email_sel, f"Proposta Fotovoltaico - {df['corp']['name']}", anteprima):
            st.balloons()
            st.success(f"Email inviata a {email_sel}!")
