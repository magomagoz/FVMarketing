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

# --- 1. IDENTIFICAZIONE DESTINATARIO ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # Recuperiamo il lead selezionato (o il primo della lista)
    if data.get('leads'):
        opzioni_l = [f"{l['name']}" for l in data['leads']]
        sel_l = st.selectbox("🎯 Conferma il destinatario:", opzioni_l)
        lead_scelto = data['leads'][opzioni_l.index(sel_l)]
        nome_destinatario = lead_scelto['name'].split(' ')[0] # Prende solo il primo nome
    else:
        nome_destinatario = "Direttore"

    # --- 2. SINCRONIZZAZIONE BOZZA ---
    # Inizializziamo la bozza nell'editor con il nome CORRETTO
    testo_base = f"Gentile {nome_destinatario},\n\nLe scrivo perché ora l'impianto fotovoltaico per {data['corp']['name']} potrà beneficiare dell'IperAmmortamento 2026..."
    
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = testo_base

    st.divider()

    # --- 3. EDITOR (Sorgente dati) ---
    st.subheader("📧 Personalizza la Comunicazione")
    with st.expander("📝 Clicca qui per modificare il testo della mail", expanded=True):
        # L'area di testo deve leggere e scrivere sempre in session_state
        testo_chiaro = st.text_area(
            "Contenuto mail:", 
            value=st.session_state.bozza_editor, 
            height=300,
            key="main_text_area"
        )
        st.session_state.bozza_editor = testo_chiaro

    # --- 4. ANTEPRIMA (Riflette l'editor) ---
    st.subheader("✍️ Controlla e Invia")
    
    # Trasformiamo i ritorni a capo dell'editor in tag HTML per l'anteprima
    testo_html_sincronizzato = st.session_state.bozza_editor.replace("\n", "<br>")
    
    # Generiamo l'anteprima finale usando il testo appena modificato
    anteprima_finale = mailer.generate_body('email_dg.html', {
        'corpo_testuale': testo_html_sincronizzato
    })

    with st.container(border=True):
        st.components.v1.html(anteprima_finale, height=400, scrolling=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            test_m = st.text_input("Mail test:", value="tua@mail.it")
            if st.button("🧪 INVIA TEST"):
                if mailer.send_mail(test_m, "Test", anteprima): st.toast("Inviata!")
        with col_btn2:
            st.write(" ")
            if st.button("🚀 INVIA AL CLIENTE", type="primary"):
                st.balloons()
