import os
import shutil

import urllib
import urlfetch

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
import time
import json
import actions
import bot

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
driver = webdriver.Firefox(profile)
driver.get("https://web.whatsapp.com/")
with open('selectores.json', 'rb') as selectors:
    selectors = json.load(selectors)

while True:
    try:
        e = driver.switch_to.active_element
        print(e.get_attribute("class"))
        emogis = e.find_elements_by_xpath(selectors["emogi_container"])
        print(len(emogis))
        text = ''
        for ec in emogis:
            ec.get_attribute("class")
            text += ec.find_element_by_xpath(".//img").get_attribute("data-plain-text")
        print(text)
    except Exception as e:
        print(e)
    
    time.sleep(3)
