import smtplib
from module import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send(subject, recipients, message):

    # ---------compose-------
    msg = MIMEMultipart()
    msg.attach(MIMEText(message, 'html'))

    msg['Subject'] = subject
    msg['From'] = '%s <%s>' % (config['SMTP_SENDER'], config['SMTP_LOGIN'])
    if config['APP_STAGE'] == 'PRODUCTION':
        msg['To'] = ', '.join(recipients)
    else:
        msg['To'] = config['SMTP_LOGIN']
        recipients = [config['SMTP_LOGIN']]

    # ---------send-------
    server = smtplib.SMTP(config['SMTP_HOST'], config['SMTP_PORT'])
    server.ehlo()
    server.starttls()
    server.login(config['SMTP_LOGIN'], config['SMTP_PASSWORD'])
    server.sendmail(config['SMTP_LOGIN'], recipients, msg.as_string())
    server.quit()
