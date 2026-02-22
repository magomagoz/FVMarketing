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

        if st.session_state.get('companies'):
            st.write("Seleziona quella corretta:")
            # Creiamo etichette chiare per la scelta
            labels = [f"🏢 {c['name']} ({c['piva']})" for c in st.session_state.companies]
            scelta_idx = st.radio("Risultati:", range(len(labels)), format_func=lambda x: labels[x], key="radio_sel")
            
            if st.button("🚀 ANALIZZA SELEZIONATA"):
                azienda = st.session_state.companies[scelta_idx]
                with st.spinner("Analisi in corso..."):
                    leads = search_decision_maker(azienda['name'])
                    st.session_state.data_found = {
                        "corp": azienda,
                        "leads": leads
                    }
                    if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
                st.rerun()

# --- 1. SCHEDA AZIENDA SOTTO IL BANNER ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # Questo blocco visualizza P.IVA, Fatturato e Località proprio sotto il banner
    with st.container(border=True):
        st.markdown(f"### 📊 Analisi Aziendale: {data['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", data['corp'].get('piva', 'Da verificare'))
        with c2: st.metric("💰 Fatturato Est.", data['corp'].get('revenue', 'Non disponibile'))
        with c3: st.metric("📍 Località", data['corp'].get('location', 'N.D.')[:30] + "...")
    
    st.divider()

    # --- 2. SELEZIONE CONTATTO ---
    if data.get('leads'):
        st.subheader("👥 Decision Maker individuati")
        opzioni_l = [f"{l['name']} ({l['source']})" for l in data['leads']]
        
        # Usiamo una key per mantenere la selezione fissa
        sel_l = st.selectbox("🎯 Invia a questo contatto:", opzioni_l, key="sel_lead_finale")
        index_lead = opzioni_l.index(sel_l)
        lead_attuale = data['leads'][index_all]
        
        # Puliamo il nome per il "Gentile" (es. "Mario Rossi" -> "Mario")
        nome_per_mail = lead_attuale['name'].split(' ')[0]
    else:
        st.warning("Nessun contatto trovato.")
        nome_per_mail = "Direttore"

    # --- 3. LOGICA EDITOR E NOME ---
    # Prepariamo il testo base con il nome corretto
    testo_base = f"Gentile {nome_per_mail},\n\nLe scrivo perché ora l'impianto fotovoltaico per {data['corp']['name']} potrà beneficiare dell'IperAmmortamento 2026..."
    
    # Inizializziamo l'editor solo se è vuoto o se il nome è diverso da quello selezionato
    if 'bozza_editor' not in st.session_state or nome_per_mail not in st.session_state.bozza_editor:
        st.session_state.bozza_editor = testo_base

    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=True):
        testo_chiaro = st.text_area(
            "Contenuto:", 
            value=st.session_state.bozza_editor, 
            height=250,
            key="area_testo_mail"
        )
        # Salviamo la modifica manuale in session_state
        st.session_state.bozza_editor = testo_chiaro

    # --- 4. ANTEPRIMA HTML SINCRONIZZATA ---
    st.subheader("✍️ Anteprima e Invio")
    
    # L'anteprima deve leggere DIRETTAMENTE quello che c'è nell'editor sopra
    testo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    
    anteprima = mailer.generate_body('email_dg.html', {
        'corpo_testuale': testo_html
    })

    with st.container(border=True):
        st.components.v1.html(anteprima, height=350, scrolling=True)
        
        col1, col2 = st.columns(2)
        with col1:
            test_m = st.text_input("Tua mail per test:", value="tua@mail.it")
            if st.button("🧪 INVIA TEST"):
                if mailer.send_mail(test_m, f"Test Proposta {data['corp']['name']}", anteprima):
                    st.toast("Mail di test inviata con successo!")
        with col2:
            st.write(" ")
            if st.button("🚀 INVIA AL CLIENTE", type="primary"):
                # Qui andrebbe l'indirizzo reale trovato dallo scraper
                st.balloons()
