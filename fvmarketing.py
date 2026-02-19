import streamlit as st
import time
from validator import validate_piva_vies
from scraper import search_decision_maker, get_verified_email
from mailer import Mailer

# Configurazione Mailer (Mock per il test)
mailer = Mailer("smtp.gmail.com", 465, "test@test.it", "password")

st.image("banner.png", use_container_width=True)
#st.title("🚀 Business Lead Finder")

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
# --- FASE 3: VISUALIZZAZIONE E DECISIONE ---
if st.session_state.data_found:
    data = st.session_state.data_found
    
    # ... (tieni pure le tue colonne col1 e col2 per i dati aziendali) ...

    st.divider()
    st.subheader("📧 Personalizza la Comunicazione")

    # --- QUI INSERISCI IL PUNTO 1 (LOGICA PULITA E COMPRIMIBILE) ---
    
    # 1. Prepariamo la bozza iniziale "pulita" solo se non esiste già
    nome_destinatario = data['lead']['name'] if data['lead'] else "Direttore"
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = f"Gentile {nome_destinatario},\n\nLe scrivo perché seguo con interesse {data['corp']['name']}..."

    # 2. BOX COMPRIMIBILE (PUNTO 1)
    with st.expander("📝 Clicca qui per modificare il testo della mail", expanded=False):
        testo_chiaro = st.text_area(
            "Edita il contenuto (scrivi normalmente senza tag HTML):", 
            value=st.session_state.bozza_editor, 
            height=300
        )
        # Aggiorniamo lo stato così la modifica "resta"
        st.session_state.bozza_editor = testo_chiaro

    # 3. TRASFORMAZIONE PER L'INVIO (Per far arrivare bene la mail di prova)
    # Trasformiamo i ritorni a capo in tag HTML <br> per il Mailer
    testo_formattato = testo_chiaro.replace("\n", "<br>")
    
    # Generiamo l'HTML finale inserendo il testo nella "cornice" del template
    anteprima_finale_html = mailer.generate_body('email_dg.html', {
        'corpo_testuale': testo_formattato
    })

    st.subheader("✍️ Controlla e Invia")
    
    # 4. ANTEPRIMA DINAMICA
    with st.container(border=True):
        st.caption("👁️ Anteprima finale (quello che riceverà il cliente)")
        st.components.v1.html(anteprima_finale_html, height=350, scrolling=True)

        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            test_email = st.text_input("Tua mail per il test:", value="tua_mail@esempio.it")
            if st.button("🧪 INVIA TEST A ME", use_container_width=True):
                if test_email:
                    with st.spinner("Invio test..."):
                        # Usiamo anteprima_finale_html così arriva formattata bene!
                        successo = mailer.send_mail(
                            test_email, 
                            f"[TEST] Proposta per {data['corp']['name']}", 
                            anteprima_finale_html
                        )
                        if successo:
                            st.toast("Mail di test inviata!", icon="📩")
                else:
                    st.error("Inserisci un indirizzo per il test")
        
        with c2:
            st.write(" ") 
            st.write(" ") 
            if st.button("🚀 INVIA AL CLIENTE", type="primary", use_container_width=True):
                with st.spinner("Invio al DG..."):
                    successo = mailer.send_mail(
                        data['email'], 
                        f"Domanda rapida per {data['corp']['name']}", 
                        anteprima_finale_html
                    )
                    if successo:
                        st.balloons()
                        st.success(f"Inviata a {data['lead']['name']}!")
