import zeep
from requests import Session
from zeep.transports import Transport

def validate_piva_vies(vat_number, country_code='IT'):
    """
    Interroga il sistema VIES per verificare l'esistenza della P.IVA.
    Restituisce un dizionario con i dati aziendali o None se non valida.
    """
    # Rimuove eventuali spazi o prefissi IT inseriti per errore
    vat_clean = vat_number.replace(" ", "").replace("IT", "")
    
    # URL del servizio SOAP ufficiale europeo
    wsdl_url = 'https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'
    
    # Configurazione del timeout (essenziale per non bloccare il programma)
    session = Session()
    session.timeout = 15 
    transport = Transport(session=session)
    
    try:
        client = zeep.Client(wsdl=wsdl_url, transport=transport)
        # Chiamata al metodo checkVat
        result = client.service.checkVat(countryCode=country_code, vatNumber=vat_clean)
        
        if result.valid:
            # Marketing Touch: Trasformiamo da "AZIENDA SPA" a "Azienda Spa"
            # per rendere la mail più naturale
            nome_formattato = result.name.title() if result.name else "N/A"
            indirizzo_pulito = result.address.replace("\n", ", ").title() if result.address else "N/A"
            
            return {
                "valid": True,
                "name": nome_formattato,
                "address": indirizzo_pulito,
                "vat": vat_clean
            }
        else:
            return {"valid": False, "reason": "P.IVA non valida o cessata"}

    except Exception as e:
        # Gestione errori di connessione (es. server VIES offline)
        return {"valid": False, "reason": f"Errore di connessione: {str(e)}"}

# Test rapido del modulo
if __name__ == "__main__":
    test_piva = "00742640154" # Eni S.p.A.
    print(f"Test validazione P.IVA: {test_piva}")
    print(validate_piva_vies(test_piva))
