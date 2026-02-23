import streamlit as st
import time
from validator import validate_piva_vies
from scraper import search_decision_maker, get_verified_email
from mailer import Mailer

# --- CONFIGURAZIONE ---
# Usa st.secrets per non scrivere la password in chiaro su GitHub!
mailer = Mailer("smtp.gmail.com", 465, "tua_mail@gmail.com", "tua_password_app")

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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Dati Aziendali")
        st.write(f"**Ragione Sociale:** {data['corp']['name']}")
        st.write(f"**Indirizzo:** {data['corp']['address']}")
    
    with col2:
        st.subheader("👥 Decision Maker")
        # Usiamo i leads salvati nello stato
        if data.get('leads'):
            opzioni = [f"{l['name']} ({l['source']})" for l in data['leads']]
            scelta = st.selectbox("Seleziona destinatario:", opzioni)
            index_scelto = opzioni.index(scelta)
            data['lead'] = data['leads'][index_scelto]
            
            with st.expander("Dettagli profilo"):
                st.write(f"📝 *{data['lead']['snippet']}*")
                st.link_button(f"Vai al profilo {data['lead']['source']}", data['lead']['link'])
        else:
            st.warning("Nessun profilo social trovato.")
            data['lead'] = None

    st.divider()
    st.subheader("📧 Personalizza la Comunicazione")

    # 1. Logica Bozza Pulita
    nome_dest = data['lead']['name'] if data.get('lead') else "Direttore"
    corpo_default = f"Gentile {nome_dest},\n\nLe scrivo perché seguo con interesse {data['corp']['name']}..."
    
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = corpo_default

    # 2. BOX COMPRIMIBILE (Modifica)
    with st.expander("📝 Clicca qui per modificare il testo della mail", expanded=False):
        testo_chiaro = st.text_area(
            "Contenuto mail:", 
            value=st.session_state.bozza_editor, 
            height=250
        )
        st.session_state.bozza_editor = testo_chiaro

    # 3. Trasformazione HTML
    testo_formattato = testo_chiaro.replace("\n", "<br>")
    anteprima_html = mailer.generate_body('email_dg.html', {'corpo_testuale': testo_formattato})

    # 4. ANTEPRIMA E INVIO
    st.subheader("✍️ Controlla e Invia")
    with st.container(border=True):
        st.components.v1.html(anteprima_html, height=350, scrolling=True)

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
