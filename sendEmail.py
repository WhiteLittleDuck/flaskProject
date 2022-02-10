#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
# mail_host = "smtp.qq.com"  # 设置服务器
mail_host = "smtp-mail.outlook.com"
mail_user = "1318096335"  # 用户名
mail_pass = "ugvqchekuskibadi"  # 口令

sender = '1318096335@qq.com'
receivers = ['11811031@mail.sustech.edu.cn']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

message = MIMEText('Reply when you receive', '长江长江我是黄河', 'utf-8')
message['From'] = Header("WhiteLittleDuck", 'utf-8')
message['To'] = Header("test", 'utf-8')

subject = 'Python SMTP 邮件测试'
message['Subject'] = Header(subject, 'utf-8')

# try:
smtpObj = smtplib.SMTP()
smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
smtpObj.login(mail_user, mail_pass)
smtpObj.sendmail(sender, receivers, message.as_string())
print('success')
