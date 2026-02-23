import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Setup
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])
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
                    # Passiamo il nome pulito allo scraper
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
        [data-testid="stMetricValue"] {
            font-size: 16px !important; /* Leggermente più piccolo per far stare l'indirizzo */
            white-space: normal !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 13px !important;
        }
        </style>
        """, unsafe_allow_html=True)

# ... (parte iniziale del tuo fvmarketing.py rimane uguale) ...

if st.session_state.get('data_found'):
    df = st.session_state.data_found
    
    # DATI AZIENDALI (Metriche rimpicciolite)
    with st.container(border=True):
        st.subheader(f"📊 {df['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", df['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", df['corp']['revenue'])
        with c3: st.metric("📍 Sede Legale", df['corp']['location'])

    # REFERENTI
    st.subheader("👥 Referente per la comunicazione")
    nomi_leads = [f"{l['name']} ({l['source']})" for l in df['leads']]
    sel_lead = st.selectbox("🎯 Destinatario:", nomi_leads)
    
    lead_scelto = df['leads'][nomi_leads.index(sel_lead)]
    nome_gentile = lead_scelto['name'].split()[0] if lead_scelto['name'] != "Direttore Generale" else "Direttore"

        # Stringa corretta con triple virgolette per evitare errori
    testo_base = f"""Gentile {nome_gentile},

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

Le informazioni contenute nella presente comunicazione e i relativi allegati possono essere riservate e sono, comunque, destinate esclusivamente alle persone o alla Società sopraindicati. La diffusione, distribuzione e/o copiatura del documento trasmesso da parte di qualsiasi soggetto diverso dal destinatario è proibita."""

    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = testo_base

    # NOTA: expanded=False lo rende chiuso all'avvio
    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=False):
        testo_chiaro = st.text_area("Contenuto:", value=st.session_state.bozza_editor, height=250)
        st.session_state.bozza_editor = testo_chiaro

    # ANTEPRIMA (Sempre visibile per controllo rapido)
    st.subheader("✍️ Anteprima")
    corpo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': corpo_html})
    
    with st.container(border=True):
        st.components.v1.html(anteprima, height=400, scrolling=True)
        if st.button("🚀 INVIA ORA", type="primary"):
            st.balloons()
            st.success("Mail inviata con successo!")

    if 'bozza_editor' not in st.session_state or nome_gentile not in st.session_state.bozza_editor:
        st.session_state.bozza_editor = testo_base

    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=True):
        testo_chiaro = st.text_area("Contenuto:", value=st.session_state.bozza_editor, height=300)
        st.session_state.bozza_editor = testo_chiaro

    st.subheader("✍️ Anteprima")
    corpo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': corpo_html})
    
    with st.container(border=True):
        st.components.v1.html(anteprima, height=450, scrolling=True)
        if st.button("🚀 INVIA ORA", type="primary"):
            st.balloons()
