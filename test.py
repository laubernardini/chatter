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

text = ""

with open('mime_types.txt', 'rb') as mime:
    bot.MIME_TYPES = str(mime.read())

profile = webdriver.FirefoxProfile()
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.dir", bot.DOWNLOAD_PATH)
profile.set_preference("browser.download.useDownloadDir", True)
profile.set_preference("browser.download.viewableInternally.enabledTypes", "")
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", bot.MIME_TYPES)
profile.set_preference("pdfjs.disabled", True)
options = webdriver.firefox.options.Options()
options.headless = True
driver = webdriver.Firefox(profile, options=options)
driver.get("https://web.whatsapp.com/")
with open('selectores.json', 'rb') as selectors:
    selectors = json.load(selectors)
# Registrar inicio
bot.START_DATE = datetime.now()
print("inicio: ", str(bot.START_DATE))
driver.save_screenshot('qr.png')
# Proximo reload
bot.NEXT_RELOAD = bot.START_DATE + timedelta(seconds=30)
print("next: ", str(bot.NEXT_RELOAD))
r = None
while r == True:
    try:
        print("ahora: ", str(datetime.now()))
        if datetime.now() >= bot.NEXT_RELOAD:
            driver.refresh()
            bot.NEXT_RELOAD = datetime.now() + timedelta(seconds=20)
            print("next: ", str(bot.NEXT_RELOAD))
    except Exception as e:
        print(e)
    
    time.sleep(5)
