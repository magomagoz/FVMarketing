import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Setup
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
    
    # Dashboard Azienda
    with st.container(border=True):
        st.subheader(f"🏢 {df['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", df['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", df['corp']['revenue'])
        with c3: st.metric("📍 Città", df['corp']['location'])

    st.subheader("👥 Contatti individuati (Priorità Titolari)")
    # Mostriamo nella selectbox anche se è un profilo LinkedIn o FB
    nomi_leads = [f"{l['name']} [{l['source']}]" for l in df['leads']]
    sel_box = st.selectbox("🎯 Seleziona il destinatario della mail:", nomi_leads)
    lead_scelto = df['leads'][nomi_leads.index(sel_box)]    
    nome_gentile = lead_scelto['name'].split()[0] if "Direttore" not in lead_scelto['name'] else "Direttore"

    # 3. Gestione Email
    with st.expander("📧 VEDI EMAIL TROVATE", expanded=False):
        email_selezionata = st.radio("Seleziona quella corretta:", lead_scelto['emails'])
    
    # 4. Modifica Testo (CHIUSO)
    testo_base = f"""Gentile {nome_gentile},

Le scrivo perché ora l'impianto fotovoltaico per la sua Azienda potrà beneficiare dell'IperAmmortamento 2026, che le permetterà di recuperare il 67% del suo investimento in Credito d'Imposta, immediatamente esigibile già dal 2027.

In allegato troverà una simulazione di impianto fotovoltaico con il ROI che le agevolazioni permettono.

Un cordiale saluto.

Enrico Magostini
SUN ECO POWER S.r.l."""

    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = testo_base

    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=False):
        st.session_state.bozza_editor = st.text_area("Contenuto:", value=st.session_state.bozza_editor, height=250)

    # 5. Anteprima HTML
    st.subheader("✍️ Anteprima")
    corpo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    anteprima_html = mailer.generate_body('email_dg.html', {'corpo_testuale': corpo_html})
    st.components.v1.html(anteprima_html, height=300, scrolling=True)

    # 6. Invio Finale
    st.divider()
    destinatario_finale = st.text_input("📧 Destinatario finale (Controlla o modifica):", value=email_selezionata)

    if st.button("🚀 INVIA ORA", type="primary", use_container_width=True):
        if destinatario_finale:
            with st.spinner("Invio in corso..."):
                if mailer.send_mail(destinatario_finale, f"Proposta Fotovoltaico - {df['corp']['name']}", anteprima_html):
                    st.balloons()
                    st.success(f"Email inviata con successo a {destinatario_finale}!")
                else:
                    st.error("Errore nell'invio. Verifica la Password per le App nei Secrets.")
