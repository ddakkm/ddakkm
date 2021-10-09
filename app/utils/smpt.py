import smtplib
from email.mime.text import MIMEText

from pydantic import EmailStr

from app.core.config import settings


def email_sender(subject: str, text: str, to: EmailStr):
    smtp = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
    smtp.set_debuglevel(1)
    smtp.ehlo()
    smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['To'] = to
    msg['FROM'] = settings.SMTP_USER
    smtp.sendmail(settings.SMTP_USER, to, msg.as_string())
    smtp.quit()
    return {"stauts": 200, "mail_subject": subject}


if __name__ == "__main__":
    email_sender("test", "test", EmailStr("ddhyun93@gmail.com"))
