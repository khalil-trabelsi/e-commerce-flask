import os
from dotenv import load_dotenv
from logging import getLogger

from flask_mail import Message
from src import mail
load_dotenv()

logger = getLogger(__name__)

def send_email(to, subject, body):
    msg = Message(
        subject,
        recipients=[to],
        html=body,
        sender=os.getenv("MAIL_USERNAME")
    )
    logger.info(os.getenv("MAIL_USERNAME"))
    logger.info(os.getenv("MAIL_PASSWORD"))
    mail.send(msg)