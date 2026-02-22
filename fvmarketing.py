import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Setup
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])
st.set_page_config(layout="wide")
st.image("banner.png", use_container_width=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Ricerca Azienda")
    query = st.text_input("Inserisci Nome Azienda", key="input_query")
    
    if query:
        if 'companies' not in st.session_state or st.session_state.get('last_q') != query:
            st.session_state.companies = search_company_list(query)
            st.session_state.last_q = query

        if st.session_state.companies:
            labels = [f"🏢 {c['name']} ({c['piva']})" for c in st.session_state.companies]
            idx = st.radio("Seleziona:", range(len(labels)), format_func=lambda x: labels[x])
            
            if st.button("🚀 ANALIZZA SELEZIONATA"):
                with st.spinner("Cercando referenti..."):
                    st.session_state.data_found = {
                        "corp": st.session_state.companies[idx],
                        "leads": search_decision_maker(st.session_state.companies[idx]['name'])
                    }
                    if 'bozza_editor' in st.session_state: del st.session_state.bozza_editor
                st.rerun()

        else:
            st.warning("Nessuna azienda trovata con P.IVA. Prova a cambiare nome.") # <--- Aggiungi questo

# --- MAIN ---
if st.session_state.get('data_found'):
    df = st.session_state.data_found
    
    # DATI AZIENDALI
    with st.container(border=True):
        st.subheader(f"📊 {df['corp']['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🆔 Partita IVA", df['corp']['piva'])
        with c2: st.metric("💰 Fatturato Est.", df['corp']['revenue'])
        with c3: st.metric("📍 Località", df['corp']['location'])

    # REFERENTI
    st.subheader("👥 Referente per la comunicazione")
    # Qui Monica Diaz Gonzales riapparirà nella lista
    nomi_leads = [f"{l['name']} ({l['source']})" for l in df['leads']]
    sel_lead = st.selectbox("🎯 Destinatario:", nomi_leads)
    
    # FIX INDICI: trova il lead corretto in modo sicuro
    lead_scelto = df['leads'][nomi_leads.index(sel_lead)]
    nome_gentile = lead_scelto['name'].split()[0] if lead_scelto['name'] != "Direttore Generale" else "Direttore"

    # EDITOR (Correzione NameError)
    testo_base = f"Gentile {nome_gentile},\n\nLe scrivo perché ora l'impianto fotovoltaico per la sua Azienda potrà beneficiare dell'IperAmmortamento 2026, che le permetterà di recuperare il 67% del suo investimento in Credito d'Imposta, immediatamente esigibile già dal 2027.\n\n

    In allegato troverà una simulazione di impianto fotovoltaico con il ROI che le agevolazioni permettono: potrà vedere come l'investimento si ripaga immediatamente, grazie al risparmio energetico e all'IperAmmortamento 2026.\n\n

    Vorrei avere l'opportunità di analizzare i suoi consumi per proporle, senza nessun impegno, il corretto Ritorno sull'Investimento.\n\n

    Non esiti nel contattarmi per ogni delucidazione in merito.\n\n
    
    Un cordiale saluto.\n\n
    
    Enrico Magostini\n\n
    Consulente Energetico\n\n

    SUN ECO POWER S.r.l.\n\n
    Mobile:    +39 334 607 9956\n\n 
    e-mail:    e.magostini@sunecopower.it\n\n  
    P.IVA/C.F:01870010855\n\n
    REA: CL-104471\n\n
 
    www.sunecopower.it\n\n
 
    Le informazioni contenute nella presente comunicazione e i relativi allegati possono essere <br> 
    riservati e sono, comunque, destinati esclusivamente alle persone o alla Società sopraindicati.<br>
    La diffusione, distribuzione e/o copiatura del documento trasmesso da parte di qualsiasi <br> 
    soggetto diverso dal destinatario è proibita, sia ai sensi dell'art. 616 c.p., sia ai sensi<br>
    del D. Lgs. n. 196/2003. Se avete ricevuto questo messaggio per errore, vi preghiamo di<br>
    distruggerlo e di informarci immediatamente inviando un messaggio all'indirizzo e-mail:<br> 
    info@sunecopower.it\n\n"
    
    if 'bozza_editor' not in st.session_state or nome_gentile not in st.session_state.bozza_editor:
        st.session_state.bozza_editor = testo_base

    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=True):
        testo_chiaro = st.text_area("Contenuto:", value=st.session_state.bozza_editor, height=200)
        st.session_state.bozza_editor = testo_chiaro

    # ANTEPRIMA (Sincronizzata)
    st.subheader("✍️ Anteprima")
    corpo_html = st.session_state.bozza_editor.replace("\n", "<br>")
    anteprima = mailer.generate_body('email_dg.html', {'corpo_testuale': corpo_html})
    
    with st.container(border=True):
        st.components.v1.html(anteprima, height=350, scrolling=True)
        if st.button("🚀 INVIA ORA", type="primary"):
            st.balloons()
