import streamlit as st
import time
from validator import validate_piva_vies
from scraper import search_decision_maker, get_verified_email
from mailer import Mailer

# --- CONFIGURAZIONE ---
# Usa st.secrets per non scrivere la password in chiaro su GitHub!
#mailer = Mailer("smtp.gmail.com", 465, "tua_mail@gmail.com", "tua_password_app")

# In fvmarketing.py (all'inizio)
mailer = Mailer(
    host="smtp.gmail.com", 
    port=465, 
    user=st.secrets["MAIL_USER"], 
    password=st.secrets["MAIL_PASSWORD"]
)

st.image("banner.png", use_container_width=True)

if 'data_found' not in st.session_state:
    st.session_state.data_found = None

# --- FASE 1: INPUT (Sidebar) ---
with st.sidebar:
    st.header("Ricerca Azienda")
    company_input = st.text_input("Nome Azienda o P.IVA")
    search_button = st.button("Analizza Azienda")

# --- FASE 2: ELABORAZIONE ---
if search_button and company_input:
    with st.spinner("Recupero informazioni in corso..."):
        if company_input.isdigit():
            info_corp = validate_piva_vies(company_input)
        else:
            info_corp = {"name": company_input.title(), "address": "Indirizzo non trovato", "valid": True}

        if info_corp and info_corp.get('valid'):
            # Prima ricerca veloce per inizializzare
            leads = search_decision_maker(info_corp['name'])
            st.session_state.data_found = {
                "corp": info_corp,
                "leads": leads, # Salviamo la lista completa
                "email": "mario.rossi@azienda.it" 
            }
            # Reset della bozza quando cambia azienda
            if 'bozza_editor' in st.session_state:
                del st.session_state.bozza_editor
        else:
            st.error("Impossibile trovare dati validi.")

# --- FASE 3: VISUALIZZAZIONE ---
if st.session_state.data_found:
    data = st.session_state.data_found
    
    # 1. Creiamo le colonne SOLO per i dati in alto
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Dati Aziendali")
        st.write(f"**Ragione Sociale:** {data['corp']['name']}")
        st.write(f"**Indirizzo:** {data['corp']['address']}")
    
    with col2:
        st.subheader("👥 Decision Maker")
        if data.get('leads'):
            opzioni = [f"{l['name']} ({l['source']})" for l in data['leads']]
            scelta = st.selectbox("Seleziona destinatario:", opzioni)
            index_scelto = opzioni.index(scelta)
            # Aggiorniamo il lead selezionato nello stato
            st.session_state.data_found['lead'] = data['leads'][index_scelto]
            
            with st.expander("Dettagli profilo"):
                st.write(f"📝 *{st.session_state.data_found['lead']['snippet']}*")
        else:
            st.warning("Nessun profilo trovato.")

    # --- 2. USCIAMO DALLE COLONNE (Torniamo a tutta larghezza) ---
    st.divider()

    # Recuperiamo il nome per il "Gentile..."
    current_lead = st.session_state.data_found.get('lead')
    nome_dest = current_lead['name'] if (current_lead and current_lead.get('name')) else "Direttore"

    # Inizializziamo la bozza completa (se non esiste o se è diversa dal nome attuale)
    testo_base = f"Gentile {nome_dest},\n\nLe scrivo perché ora l'impianto fotovoltaico per {data['corp']['name']} potrà beneficiare dell'IperAmmortamento 2026..."
    
    if 'bozza_editor' not in st.session_state or nome_dest not in st.session_state.bozza_editor:
        st.session_state.bozza_editor = testo_base

    st.subheader("📧 Personalizza la Comunicazione")

    # Ora questo expander sarà largo quanto tutto lo schermo!
    with st.expander("📝 Clicca qui per modificare il testo della mail", expanded=False):
        testo_chiaro = st.text_area(
            "Contenuto mail:", 
            value=st.session_state.bozza_editor, 
            height=300
        )
        st.session_state.bozza_editor = testo_chiaro

    # 3. ANTEPRIMA E INVIO (Sempre a tutta larghezza)
    testo_formattato = testo_chiaro.replace("\n", "<br>")
    anteprima_html = mailer.generate_body('email_dg.html', {'corpo_testuale': testo_formattato})

    st.subheader("✍️ Controlla e Invia")
    with st.container(border=True):
        st.components.v1.html(anteprima_html, height=400, scrolling=True)
        
        # ... qui metti i tuoi bottoni c1, c2 per l'invio ...
    
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            test_email = st.text_input("Mail per test:", value="tua_mail@gmail.com")
            if st.button("🧪 INVIA TEST", use_container_width=True):
                with st.spinner("Invio..."):
                    if mailer.send_mail(test_email, f"[TEST] per {data['corp']['name']}", anteprima_html):
                        st.toast("Test inviato!", icon="📩")
        
        with c2:
            st.write(" ")
            st.write(" ")
            if st.button("🚀 INVIA AL CLIENTE", type="primary", use_container_width=True):
                with st.spinner("Invio..."):
                    if mailer.send_mail(data['email'], f"Proposta per {data['corp']['name']}", anteprima_html):
                        st.balloons()
                        st.success("Inviata!")
