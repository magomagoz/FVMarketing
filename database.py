import sqlite3
from datetime import datetime

def get_connection():
    """Ritorna una connessione al database locale."""
    return sqlite3.connect('marketing_leads.db')

def init_db():
    """Inizializza le tabelle se non esistono."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabella Aziende (Anagrafica da CCIAA/VIES)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            vat_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            website TEXT,
            industry TEXT,
            created_at DATETIME
        )
    ''')
    
    # Tabella Lead (I contatti trovati via scraping)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vat_number TEXT,
            full_name TEXT,
            role TEXT,
            email TEXT UNIQUE,
            status TEXT DEFAULT 'new', -- new, contacted, bounced, interested
            last_contacted DATETIME,
            FOREIGN KEY (vat_number) REFERENCES companies (vat_number)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("🗄️ Database inizializzato correttamente.")

def save_company(piva, nome, indirizzo):
    """Salva o aggiorna i dati dell'azienda."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT OR REPLACE INTO companies (vat_number, name, address, created_at)
        VALUES (?, ?, ?, ?)
    ''', (piva, nome, indirizzo, now))
    
    conn.commit()
    conn.close()

def save_lead(piva, nome_dg, email_dg, ruolo="Direttore Generale"):
    """Salva il contatto trovato per l'azienda."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO leads (vat_number, full_name, email, role)
            VALUES (?, ?, ?, ?)
        ''', (piva, nome_dg, email_dg, ruolo))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # L'email esiste già, evitiamo duplicati
        return False
    finally:
        conn.close()

# Esegui l'inizializzazione al primo avvio
if __name__ == "__main__":
    init_db()
