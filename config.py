#!/usr/bin/env python
# encoding: utf-8
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

MONGO_SETTINGS = {
    "host": "localhost",
    "port": 27017,
    "database":"bt_tornado"
}

GMAIL_CONFIG = {
    'mail_host': "smtp.gmail.com",
    'mail_port': 25,
    'mail_user': "zhkzyth",
    'mail_pass': "",
    'mail_postfix': "gmail.com",
}

try:
    from local_config import *
except:
    pass
