#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
 
server_login='ncuelectronic@foxmail.com'    # 发件人邮箱账号
server_pass = 'qgakfjvzmfnkdagb'              # 发件人邮箱密码

sender_addr = "ncuelectronic@foxmail.com"
sernder_name = "NCU电赛基地"

receiver_addr ='luoyusang2007@hotmail.com'      # 收件人邮箱账号
receiver_name = "Dear XXX"


def mail():
    ret=True
    try:
        msg=MIMEText('测试邮件内容','plain','utf-8')
        msg['From']=formataddr([sernder_name,sender_addr])     # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To']=formataddr([receiver_name,receiver_addr])                          # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        # msg['To']=formataddr([receiver_name,'receiver_addr@stupid.com'])                          # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject']="Test-Nothing"                                                # 邮件的主题，也可以说是标题
 
        server=smtplib.SMTP_SSL("smtp.qq.com", 465)                                  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(server_login, server_pass)                                      # 括号中对应的是发件人邮箱账号、邮箱密码
        
        server.sendmail(server_login,[receiver_addr,],msg.as_string())               # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret=False
    return ret
 
ret=mail()
if ret:
    print("邮件发送成功")
else:
    print("邮件发送失败")