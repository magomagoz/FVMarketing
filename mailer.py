import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2

class Mailer:
    def __init__(self, server, port, user, password):
        self.server = server
        self.port = port
        self.user = user
        self.password = password

    def generate_body(self, template_path, data):
        with open(template_path, 'r', encoding='utf-8') as f:
            template = jinja2.Template(f.read())
        return template.render(data)

    def send_mail(self, receiver_email, subject, body_html):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body_html, 'html'))

            # Per la porta 465 usiamo SMTP_SSL
            with smtplib.SMTP_SSL(self.server, self.port) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, receiver_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Errore: {e}")
            return False
