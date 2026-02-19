import streamlit as st
import time
from validator import validate_piva_vies
from scraper import search_decision_maker, get_verified_email
from mailer import Mailer

# Configurazione Mailer (Mock per il test)
mailer = Mailer("smtp.gmail.com", 465, "test@test.it", "password")

st.title("🚀 Business Lead Finder")

# --- FASE 1: INPUT ---
with st.sidebar:
    st.header("Ricerca Azienda")
    company_input = st.text_input("Nome Azienda o P.IVA")
    search_button = st.button("Analizza Azienda")

# Inizializziamo lo stato della sessione per "ricordare" i dati tra un click e l'altro
if 'data_found' not in st.session_state:
    st.session_state.data_found = None

# --- FASE 2: ELABORAZIONE ---
if search_button and company_input:
    with st.spinner("Recupero informazioni in corso..."):
        # Se l'input è numerico, proviamo la validazione P.IVA
        if company_input.isdigit():
            info_corp = validate_piva_vies(company_input)
        else:
            # Qui potresti aggiungere una ricerca Google per trovare la P.IVA dal nome
            # Per ora usiamo il nome direttamente per lo scraping
            info_corp = {"name": company_input.title(), "address": "Indirizzo non trovato", "valid": True}

        if info_corp and info_corp.get('valid'):
            # Cerchiamo il Direttore Generale
            lead = search_decision_maker(info_corp['name'])
            
            # Salviamo tutto nello stato della sessione
            st.session_state.data_found = {
                "corp": info_corp,
                "lead": lead,
                "email": "mario.rossi@azienda.it" # Simulazione email trovata
            }
        else:
            st.error("Impossibile trovare dati validi per questa azienda.")

# --- FASE 3: VISUALIZZAZIONE E DECISIONE ---
if st.session_state.data_found:
    data = st.session_state.data_found
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Dati Aziendali")
        st.write(f"**Ragione Sociale:** {data['corp']['name']}")
        st.write(f"**Indirizzo:** {data['corp']['address']}")
    
    with col2:
        #st.subheader("👤 Decision Maker")
        #if data['lead']:
            #st.write(f"**Nome:** {data['lead']['name']}")
            #st.write(f"**Ruolo:** Direttore Generale")
            #st.write(f"**Email:** {data['email']}")
        #else:
            #st.warning("Nessun contatto trovato.")
    
        st.subheader("👥 Possibili Decision Maker individuati")
        
        # Chiamata alla nuova funzione robusta
        leads = search_decision_maker(data['corp']['name'])
        
        if leads:
            # Creiamo un selettore per scegliere la persona corretta
            opzioni = [f"{l['name']} ({l['source']})" for l in leads]
            scelta = st.selectbox("Seleziona il destinatario della mail:", opzioni)
            
            # Recuperiamo i dettagli del lead selezionato
            index_scelto = opzioni.index(scelta)
            selected_lead = leads[index_scelto]
            
            with st.expander("Dettagli profilo trovato"):
                st.write(f"📝 *{selected_lead['snippet']}*")
                st.link_button(f"Vai al profilo {selected_lead['source']}", selected_lead['link'])
                
            # Aggiorniamo i dati per il template della mail
            data['lead'] = selected_lead
        else:
            st.warning("Nessun profilo social trovato. Verrà usato un destinatario generico.")

    
    st.divider()

    # Anteprima della Mail
    st.subheader("📧 Anteprima Comunicazione")

if st.session_state.data_found:
    # 1. Recuperiamo i dati dalla sessione
    data = st.session_state.data_found
    
    # 2. Generiamo la bozza iniziale (solo se non l'abbiamo già modificata)
    bozza_base = mailer.generate_body('email_dg.html', {
        'lead_name': data['lead']['name'] if data['lead'] else "Direttore",
        'company_name': data['corp']['name'],
        'city': "vostra sede",
        'industry': "Innovazione"
    })

    st.subheader("✍️ Personalizza e Invia")
    
    # 3. Campo di modifica (TextArea)
    # Usiamo bozza_base come valore iniziale
    testo_personalizzato = st.text_area(
        "Modifica il corpo della mail qui:", 
        value=bozza_base, 
        height=350
    )

    # 4. Anteprima DINAMICA (mostra quello che scrivi nella text_area)
    with st.container(border=True):
        st.caption("👁️ Anteprima finale (quello che riceverà il cliente)")
        st.components.v1.html(testo_personalizzato, height=300, scrolling=True)

    # 5. Bottone di invio
    if st.button("🚀 INVIA MAIL PERSONALIZZATA", type="primary", use_container_width=True):
        if not data.get('email'):
            st.error("Manca l'indirizzo email del destinatario!")
        else:
            with st.spinner("Invio in corso..."):
                # IMPORTANTE: Passiamo 'testo_personalizzato', non 'bozza_base'!
                successo = mailer.send_mail(
                    data['email'], 
                    f"Domanda rapida per {data['corp']['name']}", 
                    testo_personalizzato
                )
                
                if successo:
                    st.balloons()
                    st.success(f"✅ Mail inviata con successo a {data['lead']['name']}!")
                    # Opzionale: puliamo lo stato per una nuova ricerca
                    # st.session_state.data_found = None 
