
import smtplib
from email.mime.text import MIMEText

def send_email(html_content, recipients):
    msg = MIMEText(html_content, "html")
    msg["Subject"] = "FDA 最新藥品安全通訊摘要"
    msg["From"] = "your_email@example.com"
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.login("your_email@example.com", "password")
