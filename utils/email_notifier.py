import os
import json
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'email_config.json')

def load_config():
    default_config = {
        "sender_email": "v2573880@gmail.com",
        "sender_password": "ublclimvcsaduoli",
        "receiver_email": "953623244024@ritrjpm.ac.in",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return default_config
    return default_config

class EmailNotifier:
    def __init__(self):
        self.config = load_config()

    def _send_email_thread(self, subject, body):
        import time
        t_str = time.strftime('%H:%M:%S')
        try:
            # Re-load config each time in case it changed
            config = load_config()
            
            msg = MIMEMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = config['receiver_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            smtp_server = config['smtp_server']
            smtp_port = int(config['smtp_port'])
            
            # Choose correct protocol based on port
            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()

            server.login(config['sender_email'], config['sender_password'])
            text = msg.as_string()
            server.sendmail(config['sender_email'], config['receiver_email'], text)
            server.quit()
            print(f"[{t_str}] EMAIL SUCCESS: {subject}")
        except smtplib.SMTPAuthenticationError:
            print(f"[{t_str}] EMAIL ERROR: Auth failed for '{config['sender_email']}'. Verify App Password and 2-Step Verification.")
        except Exception as e:
            print(f"[{t_str}] EMAIL ERROR: {e}")

    def send_alert(self, alert_type, person_id, timestamp):
        subject = f"SECURITY ALERT: {alert_type} Detected"
        body = f"An anomaly has been detected by the surveillance system.\n\n" \
               f"Type: {alert_type}\n" \
               f"Person ID: {person_id}\n" \
               f"Timestamp: {timestamp}\n\n" \
               f"Please check the dashboard for more details."
        
        # Run in a separate thread to avoid blocking the main application
        threading.Thread(target=self._send_email_thread, args=(subject, body), daemon=True).start()

# Singleton instance
notifier = EmailNotifier()
