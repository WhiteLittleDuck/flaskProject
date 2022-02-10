import smtplib

MY_ADDRESS='reviewanalysis2021@outlook.com'
PASSWORD='hyrzal2021'

TO_Addr= '11811031@mail.sustech.edu.cn'

s=smtplib.SMTP(host='smtp-mail.outlook.com',port=587)
s.starttls()
s.login(MY_ADDRESS,PASSWORD)
name=['hyr']
# emails=[email]
content = 'helloha'

from email.mime.multipart import  MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

msg = MIMEMultipart()  # create a message

# add in the actual person name to the message template
message = 'this is the content of the email'
# attachment = MIMEApplication(open('backend_update.zip', 'rb').read())
# attachment.add_header('Content-Disposition', 'attachment',filename=attachment)

zipFile = 'backend_update.zip'
zipApart = MIMEApplication(open(zipFile, 'rb').read())
zipApart.add_header('Content-Disposition', 'attachment', filename=zipFile)


# setup the parameters of the message
msg['From'] = MY_ADDRESS
msg['To'] = TO_Addr
msg['Subject'] = "Hello! hyr! This is the title"

# add in the message body
msg.attach(MIMEText(message, 'plain'))
# msg.attach(attachment)
msg.attach(zipApart)

# send the message via the server set up earlier.
s.send_message(msg)
print('done')