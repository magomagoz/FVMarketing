import streamlit as st
import requests
import json

# Token OpenAPI (usa secrets.toml su GitHub)
OPENAPI_TOKEN = st.secrets["openapi_token"]
BASE_URL = "https://imprese.openapi.it"

def search_aziende(query):
    url = f"{BASE_URL}/advance"
    params = {"denominazione": query, "limit": 10, "dry_run": 0}
    headers = {"Authorization": f"Bearer {OPENAPI_TOKEN}"}
    resp = requests.get(url, params=params, headers=headers)
    return resp.json().get("data", [])

def dettagli_azienda(piva):
    url = f"{BASE_URL}/advance/{piva}"
    headers = {"Authorization": f"Bearer {OPENAPI_TOKEN}"}
    resp = requests.get(url, headers=headers)
    data = resp.json().get("data", {})
    return {
        "nome": data.get("denominazione"),
        "fatturato": data.get("bilanci", {}).get("ultimo", {}).get("fatturato"),
        "citta": data.get("comune"),
        "contatti": data.get("pec")  # Aggiungi LinkedIn search qui
    }

st.sidebar.title("Ricerca Azienda")
query = st.sidebar.text_input("Nome o P.IVA:")
if query:
    risultati = search_aziende(query)
    selezionato = st.sidebar.selectbox("Scegli:", [r["piva"] for r in risultati])
    if st.sidebar.button("Dettagli"):
        info = dettagli_azienda(selezionato)
        st.write(f"**{info['nome']}** - Fatturato: €{info['fatturato']:,} - Sede: {info['citta']}")[page:2]
        st.write("Contatti:", info["contatti"])
