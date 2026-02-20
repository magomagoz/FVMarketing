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
    st.header("🔍 Ricerca Avanzata")
    company_query = st.text_input("Nome Azienda")
    
    if company_query:
        if 'last_query' not in st.session_state or st.session_state.last_query != company_query:
            with st.spinner("Cerco aziende corrispondenti..."):
                st.session_state.found_companies = search_company_list(company_query)
                st.session_state.last_query = company_query

        if st.session_state.found_companies:
            st.write("Seleziona quella corretta:")
            options = [c['display_name'] for c in st.session_state.found_companies]
            selected_comp_name = st.radio("Risultati trovati:", options)
            
            if st.button("Analizza Azienda Selezionata"):
                # Recuperiamo l'azienda scelta
                idx = options.index(selected_comp_name)
                chosen = st.session_state.found_companies[idx]
                
                # Salviamo nello stato e procediamo allo scraping del Decision Maker
                st.session_state.data_found = {
                    "corp": {"name": chosen['display_name'], "address": chosen['snippet'], "valid": True},
                    "leads": search_decision_maker(chosen['display_name']),
                    "email": "" # Verrà cercata dopo
                }
                # Reset bozza per la nuova azienda
                if 'bozza_editor' in st.session_state:
                    del st.session_state.bozza_editor
        else:
            st.warning("Nessuna azienda trovata con questo nome.")

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
    
    # 1. Colonne in alto per i dati (CHIUDIAMOLE SUBITO DOPO)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏢 Dati Aziendali")
        st.write(f"**Ragione Sociale:** {data['corp']['name']}")
    with col2:
        st.subheader("👥 Decision Maker")
        if data.get('leads'):
            opzioni = [f"{l['name']} ({l['source']})" for l in data['leads']]
            scelta = st.selectbox("Seleziona destinatario:", opzioni)
            index_scelto = opzioni.index(scelta)
            st.session_state.data_found['lead'] = data['leads'][index_scelto]
    
    # 2. USCITA DALLE COLONNE - Torniamo a tutta larghezza
    st.divider()

    # 3. LOGICA NOME E TESTO (Sincronizzazione)
    # Recuperiamo il nome selezionato sopra
    current_lead = st.session_state.data_found.get('lead')
    nome_dest = current_lead['name'] if (current_lead and current_lead.get('name')) else "Direttore"

    # Se la bozza non esiste o abbiamo cambiato azienda, carichiamo il template
    if 'bozza_editor' not in st.session_state:
        # Generiamo la prima bozza "sporca" con il nome corretto
        st.session_state.bozza_editor = f"Gentile {nome_dest},\n\nLe scrivo perché ora l'impianto fotovoltaico per {data['corp']['name']} potrà beneficiare dell'IperAmmortamento 2026..."

    st.subheader("📧 Personalizza la Comunicazione")

    # 4. BOX DI MODIFICA (Largo)
    with st.expander("📝 Clicca qui per modificare il testo della mail", expanded=True):
        testo_chiaro = st.text_area(
            "Contenuto mail:", 
            value=st.session_state.bozza_editor, 
            height=300
        )
        # Salviamo ogni modifica fatta a mano
        st.session_state.bozza_editor = testo_chiaro

    # 5. ANTEPRIMA FINALE (Prende il testo ESATTO dell'editor sopra)
    st.subheader("✍️ Controlla e Invia")
    
    # Trasformiamo i ritorni a capo per l'HTML dell'anteprima
    testo_per_anteprima = st.session_state.bozza_editor.replace("\n", "<br>")
    
    # Passiamo il testo modificato alla cornice HTML
    anteprima_html = mailer.generate_body('email_dg.html', {
        'corpo_testuale': testo_per_anteprima
    })

    with st.container(border=True):
        # Ora l'anteprima mostrerà il nome perché glielo passiamo dentro 'corpo_testuale'
        st.components.v1.html(anteprima_html, height=400, scrolling=True)
        
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
