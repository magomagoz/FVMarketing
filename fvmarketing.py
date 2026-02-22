import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Configurazione Mailer
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])

st.set_page_config(layout="wide")
st.image("banner.png", use_container_width=True)

# --- LOGICA DI SELEZIONE NELLA SIDEBAR ---
with st.sidebar:
    st.header("🔍 Ricerca Azienda")
    query = st.text_input("Inserisci Nome Azienda", key="search_input")
    
    if query:
        # Usiamo cache per non ricaricare la lista a ogni click
        if 'last_query' not in st.session_state or st.session_state.last_query != query:
            st.session_state.companies = search_company_list(query)
            st.session_state.last_query = query

        if st.session_state.companies:
            st.write("Seleziona quella corretta:")
            labels = [f"🏢 {c['name']} ({c['piva']})" for c in st.session_state.companies]
            
            # KEY IMPORTANTE: permette di cambiare selezione senza resettare
            scelta = st.radio("Risultati:", range(len(labels)), format_func=lambda x: labels[x], key="company_radio")
            
            if st.button("🚀 ANALIZZA SELEZIONATA"):
                azienda = st.session_state.companies[scelta]
                with st.spinner("Cercando i Decision Maker..."):
                    leads = search_decision_maker(azienda['name'])
                    st.session_state.data_found = {
                        "corp": azienda,
                        "leads": leads,
                        "email": "info@azienda.it"
                    }
                    if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
                    st.rerun()

# --- VISUALIZZAZIONE DATI SOTTO IL BANNER ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # Cruscotto Dati Aziendali
    with st.container(border=True):
        st.subheader(f"📊 Scheda Azienda: {data['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", data['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", data['corp']['revenue'])
        with c3: st.metric("📍 Località", data['corp']['location'][:25] + "...")

    st.divider()

    # --- RICERCA PERSONE E MAIL ---
    if data['leads']:
        st.subheader("👥 Decision Maker individuati su LinkedIn")
        opzioni_l = [f"{l['name']}" for l in data['leads']]
        sel_l = st.selectbox("Invia a:", opzioni_l)
        lead_attuale = data['leads'][opzioni_l.index(sel_l)]
    else:
        st.warning("Nessun profilo LinkedIn trovato.")
        lead_attuale = {"name": "Direttore", "snippet": ""}

    # LOGICA EDITOR (A tutta larghezza)
    nome_dest = lead_attuale['name'].split(' - ')[0]
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = f"Gentile {nome_dest},\n\nLe scrivo perché per {data['corp']['name']}..."

    with st.expander("📝 MODIFICA MAIL", expanded=True):
        testo = st.text_area("Testo:", value=st.session_state.bozza_editor, height=250)
        st.session_state.bozza_editor = testo

    # 4. Anteprima Sincronizzata
    testo_html = testo_chiaro.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': testo_html})
    
    st.subheader("✍️ Anteprima finale")
    with st.container(border=True):
        st.components.v1.html(anteprima, height=400, scrolling=True)
        
        c1, c2 = st.columns(2)
        with c1:
            test_m = st.text_input("Mail per test:", value="tua@mail.com")
            if st.button("🧪 INVIA TEST"):
                if mailer.send_mail(test_m, "Test IperAmmortamento", anteprima):
                    st.toast("Mail inviata!")
        with c2:
            st.write(" ")
            if st.button("🚀 INVIA AL CLIENTE", type="primary"):
                if mailer.send_mail(data['email'], f"Proposta per {data['corp']['name']}", anteprima):
                    st.balloons()
