import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Inizializzazione Mailer
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])

st.set_page_config(layout="wide")
st.image("banner.png", use_container_width=True)

# ... (parti iniziali uguali) ...

# --- SIDEBAR: LISTA FILTRATA ---
if st.session_state.get('companies'):
    st.write("### 🏢 Aziende Trovate")
    # Mostriamo solo aziende che hanno una P.IVA valida
    valid_companies = [c for c in st.session_state.companies if c['piva'] != "Da verificare"]
    
    if valid_companies:
        labels = [f"{c['name']} ({c['piva']})" for c in valid_companies]
        idx = st.radio("Seleziona:", range(len(labels)), format_func=lambda x: labels[x], key="radio_clean")
        
        if st.button("🚀 ANALIZZA SELEZIONATA"):
            st.session_state.data_found = {
                "corp": valid_companies[idx],
                "leads": search_decision_maker(valid_companies[idx]['name'])
            }
            if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
            st.rerun()
    else:
        st.error("Nessuna azienda con P.IVA trovata. Riprova con un nome più specifico.")

# --- CORPO: REFERENTI PULITI ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # Visualizzazione dati sotto il banner (senza rumore)
    with st.container(border=True):
        st.subheader(f"📊 {data['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", data['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", data['corp']['revenue'])
        with c3: st.metric("📍 Località", data['corp']['location'])

    st.divider()

    # Selezione Referente (solo se utile)
    st.subheader("👥 Referente Selezionato")
    opzioni = [l['name'] for l in data['leads']]
    sel = st.selectbox("Invia a:", opzioni)
    
    # Fix Gentile: prende solo il primo nome del referente
    nome_pulito = sel.split()[0] if sel != "Direttore Generale" else "Direttore"
    
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
