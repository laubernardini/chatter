import os
import shutil

import urllib
import urlfetch
from datetime import datetime, timedelta

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
import time
import json
import actions
import bot

from os import walk

f = ['prueba_arboles.py']
new_file = None
mypath = f'inbound_file_cache{bot.OS_SLASH}{str(bot.BOT_PK)}{bot.OS_SLASH}'

for (_, _, filenames) in walk(mypath):
    for fn in filenames:
        if fn not in f:
            new_file = fn
    break

print(f"Files: {f}\nNew file: {new_file}")

