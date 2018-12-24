import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
import json
#http://naelshiab.com/tutorial-send-email-python/

secret=open("secret.json","r")
passw = json.load(secret)

fromaddr = "pepy.telegram.bot@gmail.com"
toaddr = sys.argv[1]

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Aquí tienes tu permiso!"

body = "Ha sido un placer, si tienes algo que añadir o dar feedback escribe"
"a @eskri969 en telegram. Siempre se puede mejorar :)."

msg.attach(MIMEText(body, 'plain'))

filename = sys.argv[2]
attachment = open(filename, "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, passw["mail-password"])
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
