import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Inizializzazione Mailer
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])

st.set_page_config(layout="wide")
st.image("banner.png", use_container_width=True)

# --- SIDEBAR: RICERCA E SELEZIONE ---
with st.sidebar:
    st.header("🔍 Ricerca Azienda")
    query = st.text_input("Inserisci Nome Azienda", key="input_query")
    
    if query:
        if 'last_query' not in st.session_state or st.session_state.last_query != query:
            st.session_state.companies = search_company_list(query)
            st.session_state.last_query = query

# ... (Parti iniziali del tuo codice) ...

# --- SIDEBAR: SELEZIONE AZIENDA ---
if st.session_state.get('companies'):
    st.write("### 🏢 Aziende con P.IVA trovate")
    # Filtriamo ulteriormente in interfaccia per sicurezza
    labels = [f"{c['name']} ({c['piva']})" for c in st.session_state.companies]
    scelta_idx = st.radio("Seleziona quella corretta:", range(len(labels)), format_func=lambda x: labels[x], key="radio_final_clean")
    
    if st.button("🚀 ANALIZZA SELEZIONATA"):
        azienda_scelta = st.session_state.companies[scelta_idx]
        with st.spinner("Cercando i referenti..."):
            referenti = search_decision_maker(azienda_scelta['name'])
            st.session_state.data_found = {
                "corp": azienda_scelta,
                "leads": referenti
            }
            if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
        st.rerun()

# --- CORPO: DATI E MAIL ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # Visualizzazione Dati (Box eleganti sotto il banner)
    with st.container(border=True):
        st.subheader(f"📊 {data['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", data['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", data['corp']['revenue'])
        with c3: st.metric("📍 Località", data['corp']['location'])

    st.divider()

    # Selezione Referente Umano
    st.subheader("👥 Referente per la comunicazione")
    opzioni_leads = [f"{l['name']} [{l['source']}]" for l in data['leads']]
    sel_lead = st.selectbox("🎯 Destinatario:", opzioni_leads, key="sb_final_leads")
    
    lead_attuale = data['leads'][opzioni_leads.index(sel_lead)]
    # Il nome per la mail sarà il primo nome (es: "Giulia") o "Direttore"
    nome_per_mail = lead_attuale['name'].split(' ')[0] if lead_attuale['name'] != "Direttore Generale" else "Direttore"

    # Editor e Anteprima... (Sincronizzati come nel codice precedente)
    
    # --- 3. LOGICA EDITOR E SINCRONIZZAZIONE ---
    testo_base = f"Gentile {nome_per_mail},\n\nLe scrivo perché ora l'impianto fotovoltaico per {data['corp']['name']} potrà beneficiare dell'IperAmmortamento 2026..."
    
    # Inizializziamo l'editor se vuoto o se il nome è cambiato
    if 'bozza_editor' not in st.session_state or nome_per_mail not in st.session_state.bozza_editor:
        st.session_state.bozza_editor = testo_base

    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=True):
        # Definiamo testo_chiaro esplicitamente per evitare NameError
        testo_chiaro = st.text_area(
            "Contenuto:", 
            value=st.session_state.bozza_editor, 
            height=250,
            key="area_testo_mail"
        )
        st.session_state.bozza_editor = testo_chiaro

    # --- 4. ANTEPRIMA HTML SINCRONIZZATA ---
    st.subheader("✍️ Anteprima e Invio")
    
    # L'anteprima legge dall'editor in tempo reale
    testo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    
    anteprima = mailer.generate_body('email_dg.html', {
        'corpo_testuale': testo_html
    })

    with st.container(border=True):
        st.components.v1.html(anteprima, height=400, scrolling=True)
        
        col1, col2 = st.columns(2)
        with col1:
            test_m = st.text_input("Tua mail per test:", value="tua@mail.it")
            if st.button("🧪 INVIA TEST"):
                if mailer.send_mail(test_m, f"Test Proposta {data['corp']['name']}", anteprima):
                    st.toast("Mail di test inviata!")
        with col2:
            st.write(" ")
            if st.button("🚀 INVIA AL CLIENTE", type="primary"):
                st.balloons()
