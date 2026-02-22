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

# --- CORPO PRINCIPALE: DATI E MAIL ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # 📊 SCHEDA AZIENDA SOTTO IL BANNER
    with st.container(border=True):
        st.subheader(f"Scheda Azienda: {data['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📍 Località", data['corp']['location'][:30] + "...")
        with c2: st.metric("🆔 Partita IVA", data['corp']['piva'])
        with c3: st.metric("💰 Fatturato Est.", data['corp']['revenue'])
    
    st.divider()

    # 👥 DECISION MAKER
    st.subheader("👥 Decision Maker individuati")
    opzioni_l = [f"{l['name']} ({l['source']})" for l in data['leads']]
    sel_l = st.selectbox("Invia a:", opzioni_l)
    lead_attuale = data['leads'][opzioni_l.index(sel_l)]

    # 📧 EDITOR E ANTEPRIMA
    nome_dest = lead_attuale['name'].split(' - ')[0]
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = f"Gentile {nome_dest},\n\nLe scrivo perché per {data['corp']['name']}..."

    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=True):
        # Definiamo testo_chiaro qui per evitare NameError
        testo_chiaro = st.text_area("Contenuto:", value=st.session_state.bozza_editor, height=250)
        st.session_state.bozza_editor = testo_chiaro

    # Generazione anteprima
    testo_html = testo_chiaro.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': testo_html})
    
    st.subheader("✍️ Anteprima e Invio")
    with st.container(border=True):
        st.components.v1.html(anteprima, height=350, scrolling=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            test_m = st.text_input("Mail test:", value="tua@mail.it")
            if st.button("🧪 INVIA TEST"):
                if mailer.send_mail(test_m, "Test", anteprima): st.toast("Inviata!")
        with col_btn2:
            st.write(" ")
            if st.button("🚀 INVIA AL CLIENTE", type="primary"):
                st.balloons()
