import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os

class Mailer:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        # Configurazione Jinja2 per i template
        self.env = Environment(loader=FileSystemLoader('templates'))

    def generate_body(self, template_name, data):
        """Genera l'HTML finale usando il template e i dati forniti."""
        template = self.env.get_template(template_name)
        return template.render(data)

    def send_mail(self, to_email, subject, html_content):
        """Invia la mail formattata in HTML."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attacchiamo il contenuto come HTML
            msg.attach(MIMEText(html_content, 'html'))

            # Gestione intelligente della connessione
            if self.port == 465:
                # Connessione SSL diretta (Porta 465)
                server = smtplib.SMTP_SSL(self.host, self.port)
            else:
                # Connessione TLS (Porta 587)
                server = smtplib.SMTP(self.host, self.port)
                server.starttls()
            
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            # Stampiamo l'errore per vederlo nei log di Streamlit
            print(f"ERRORE MAILER: {e}")
            return False
