#!/usr/bin/env python
# encoding: utf-8

from monitor import send_mail

if __name__ == '__main__':
    """
    test case
    """
    mailto_list=["zhkzyth@gmail.com"]

    if send_mail(mailto_list,"subject","content"):
        print "发送成功"
    else:
        print "发送失败"
