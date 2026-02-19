import zeep

def validate_piva_vies(vat_number, country_code='IT'):
    """
    Verifica se la Partita IVA è valida e attiva nel database VIES.
    """
    url = 'https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'
    client = zeep.Client(wsdl=url)
    
    try:
        result = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        if result.valid:
            print(f"✅ Azienda Trovata: {result.name}")
            return {
                "valid": True,
                "name": result.name,
                "address": result.address.replace("\n", ", ")
            }
        else:
            print("❌ Partita IVA non valida o cessata.")
            return {"valid": False}
    except Exception as e:
        print(f"⚠️ Errore durante la validazione: {e}")
        return None

# Esempio d'uso
# info_azienda = validate_piva_vies("00742640154") # P.IVA Eni S.p.A.


