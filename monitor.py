#!/usr/bin/env python
# encoding: utf-8
import smtplib
from email.mime.text import MIMEText

from config import GMAIL_CONFIG

def send_mail(to_list,sub,content):
    '''
    to_list:发给谁
    sub:主题
    content:内容
    send_mail("zhkzyth@gmail.com","sub","content")
    '''
    mail_host = GMAIL_CONFIG['mail_host']
    mail_port = GMAIL_CONFIG['mail_port']
    mail_user = GMAIL_CONFIG['mail_user']
    mail_pass = GMAIL_CONFIG['mail_pass']
    mail_postfix = GMAIL_CONFIG['mail_postfix']

    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content)
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host,mail_port)
        s.starttls()
        s.login(mail_user,mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False
