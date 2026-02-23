import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os

class Mailer:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        # Inizializza Jinja2 per caricare i template dalla cartella /templates
        self.env = Environment(loader=FileSystemLoader('templates'))

    def _format_name(self, name):
        """Trasforma 'MARIO ROSSI' in 'Mario Rossi' per un tocco umano."""
        return name.title() if name else "Direttore"

    def generate_body(self, template_name, data):
        """Genera l'HTML della mail usando il template e i dati dei lead."""
        template = self.env.get_template(template_name)
        # Formattiamo il nome del lead prima di passarlo al template
        if 'lead_name' in data:
            data['lead_name'] = self._format_name(data['lead_name'])
        return template.render(data)

    def send_mail(self, to_email, subject, html_content):
        """Invia materialmente la mail tramite SMTP."""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            print(f"✅ Email inviata con successo a: {to_email}")
            return True
        except Exception as e:
            print(f"❌ Errore durante l'invio a {to_email}: {e}")
            return False

# --- ESEMPIO DI UTILIZZO (per testare il singolo modulo) ---
if __name__ == "__main__":
    # Questi dati verranno solitamente passati dal main.py
    # Per test: usa un account Gmail (con App Password) o un servizio tipo Mailtrap
    config = {
        'server': 'smtp.gmail.com',
        'port': 465,
        'user': 'tua_mail@gmail.com',
        'pass': 'tua_password_app'
    }
    
    mailer = Mailer(config['server'], config['port'], config['user'], config['pass'])
    
    dati_lead = {
        'lead_name': 'MARIO ROSSI',
        'company_name': 'Esempio SPA',
        'industry': 'Digital Transformation',
        'city': 'Milano',
        'unsubscribe_link': 'https://tuosito.it/unsubscribe'
    }
    
    # Assicurati che il file /templates/email_dg.html esista!
    # html = mailer.generate_body('email_dg.html', dati_lead)
    # mailer.send_mail('destinatario@test.it', 'Proposta per Esempio SPA', html)
