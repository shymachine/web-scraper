import smtplib
from email.mime.text import MIMEText

def send_email(receiver_email, sender_email, sender_password, body):
    '''Send email to the receiver using Gmail SMTP server'''
    message = MIMEText(body)
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'New companies under process of liquidation'

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.close()
        print('Email sent!')
        return
    except Exception as e:
        print('Unable to sent email:', e)
        return
