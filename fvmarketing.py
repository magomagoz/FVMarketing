import streamlit as st
from scraper import search_company_list, search_decision_maker
from mailer import Mailer

# Configurazione Mailer (usa st.secrets!)
mailer = Mailer("smtp.gmail.com", 465, st.secrets["MAIL_USER"], st.secrets["MAIL_PASSWORD"])

st.set_page_config(layout="wide", page_title="AI Business Leads")
st.image("banner.png", use_container_width=True)

# Inizializza i segreti
if "SERPER_API_KEY" not in st.secrets:
    st.error("⚠️ Configura SERPER_API_KEY nei Secrets di Streamlit!")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Ricerca Azienda")
    query = st.text_input("Inserisci Nome Azienda", placeholder="Es: Ibm, Eni, Grafibox...")
    
    if query:
        with st.spinner(f"Ricerca di '{query}' in corso..."):
            aziende = search_company_list(query)
        
        if aziende:
            st.success(f"Trovate {len(aziende)} corrispondenze:")
            # Creiamo etichette che mostrano il nome e l'inizio della descrizione (per la città)
            labels = [f"🏢 {a['name']}\n{a['location'][:50]}..." for a in aziende]
            scelta_idx = st.radio("Seleziona quella corretta:", range(len(labels)), format_func=lambda x: labels[x])
            
            if st.button("✅ CONFERMA SELEZIONE"):
                # Salviamo l'azienda scelta e resettiamo lo stato per procedere
                st.session_state.data_found = {
                    "corp": {"name": aziende[scelta_idx]['name'], "address": aziende[scelta_idx]['location']},
                    "leads": search_decision_maker(aziende[scelta_idx]['name']),
                    "email": "" 
                }
                if 'bozza_editor' in st.session_state:
                    del st.session_state.bozza_editor
                st.rerun()
        else:
            st.warning("🧐 Nessun risultato trovato. Prova a scrivere il nome completo (es. 'IBM Italia').")
            if st.button("Riprova ricerca"):
                st.rerun()


# --- CORPO PRINCIPALE: EDITOR E ANTEPRIMA ---
if st.session_state.get('data_found'):
    data = st.session_state.data_found
    
    # 1. Scelta del Lead
    st.subheader(f"🎯 Destinatario per {data['corp']['name']}")
    nomi_lead = [f"{l['name']} ({l['source']})" for l in data['leads']]
    scelta_l = st.selectbox("Seleziona la persona:", nomi_lead)
    lead_sel = data['leads'][nomi_lead.index(scelta_l)]
    
    st.divider()

    # 2. Logica Nome nel Gentile
    nome_dest = lead_sel['name'] if lead_sel['name'] else "Direttore"
    
    # Inizializziamo il testo se non esiste
    if 'bozza_editor' not in st.session_state:
        st.session_state.bozza_editor = f"Gentile {nome_dest},\n\nLe scrivo perché ora l'impianto fotovoltaico per {data['corp']['name']} potrà beneficiare dell'IperAmmortamento 2026..."

    # 3. Editor (A tutta larghezza)
    with st.expander("📝 MODIFICA IL TESTO DELLA MAIL", expanded=True):
        testo_chiaro = st.text_area("Testo:", value=st.session_state.bozza_editor, height=300)
        st.session_state.bozza_editor = testo_chiaro

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
