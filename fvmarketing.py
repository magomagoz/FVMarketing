import streamlit as st
import time
from validator import validate_piva_vies
from scraper import search_decision_maker, get_verified_email
from mailer import Mailer

# Caricamento Mailer dai Secrets
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])

st.image("banner.png", use_container_width=True)

# --- FASE 1: RICERCA AZIENDA (Sidebar) ---
with st.sidebar:
    st.header("🔍 Trova Azienda")
    query = st.text_input("Inserisci nome azienda:")
    
    if query:
        with st.spinner("Ricerca in corso..."):
            aziende_trovate = search_company_list(query)
            
        if aziende_trovate:
            st.write("Qual è quella corretta?")
            # Mostriamo Nome + un pezzetto di snippet per la località
            nomi_display = [f"🏢 {a['name']} ({a['location'][:30]}...)" for a in aziende_trovate]
            scelta_idx = st.radio("Risultati:", range(len(nomi_display)), format_func=lambda x: nomi_display[x])
            
            if st.button("✅ ANALIZZA QUESTA"):
                azienda_scelta = aziende_trovate[scelta_idx]
                with st.spinner("Cerco i Decision Maker..."):
                    leads = search_decision_maker(azienda_scelta['name'])
                    st.session_state.data_found = {
                        "corp": {"name": azienda_scelta['name'], "address": azienda_scelta['location']},
                        "leads": leads,
                        "email": "info@azienda.it" # Mock
                    }
                    # Reset della bozza per la nuova azienda
                    if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
        else:
            st.warning("Nessuna azienda trovata.")

# --- FASE 2: VISUALIZZAZIONE E EDITOR ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # Intestazione pulita
    st.success(f"Analisi per: **{data['corp']['name']}**")
    
    # Selezione del Lead (se ce ne sono più di uno)
    opzioni_lead = [f"{l['name']} ({l['source']})" for l in data['leads']]
    scelta_lead = st.selectbox("🎯 Destinatario individuato:", opzioni_lead)
    lead_selezionato = data['leads'][opzioni_lead.index(scelta_lead)]
    
    st.divider()


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



    # --- EDITOR MAIL (A tutta larghezza e sincronizzato) ---
    nome_dest = lead_selezionato['name'] if lead_selezionato['name'] else "Direttore"
    
    # Carichiamo il testo base solo la prima volta
    testo_default = f"Gentile {nome_dest},\n\nLe scrivo perché ora l'impianto fotovoltaico per {data['corp']['name']}..."
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = testo_default

    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=True):
        testo_chiaro = st.text_area("Contenuto:", value=st.session_state.bozza_editor, height=300)
        st.session_state.bozza_editor = testo_chiaro

    # Anteprima HTML
    testo_html = testo_chiaro.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': testo_html})
    
    st.subheader("✍️ Anteprima e Invio")
    with st.container(border=True):
        st.components.v1.html(anteprima, height=350, scrolling=True)
        
        c1, c2 = st.columns(2)
        with c1:
            test_mail = st.text_input("Tua mail per test:", value="tua@mail.it")
            if st.button("🧪 INVIA TEST"):
                if mailer.send_mail(test_mail, "Test IperAmmortamento", anteprima):
                    st.toast("Test inviato!")
        with c2:
            st.write(" ")
            if st.button("🚀 INVIA AL CLIENTE", type="primary"):
                # Qui useresti la mail vera trovata dallo scraper
                if mailer.send_mail(data['email'], f"Proposta per {data['corp']['name']}", anteprima):
                    st.balloons()

