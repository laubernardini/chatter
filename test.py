import os
import shutil

import urllib
import urlfetch
from datetime import datetime, timedelta

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
import time, json, actions, bot

headers = {
    "Content-Type": "application/json"#"application/x-www-form-urlencoded"
}
fields = {
    "token": 1,
    "pk": 172,
    "estado": "FINALIZADO",
    "wa_id": "",
    "intentos": [
        {
            "clave": "celular",
            "cel": "5493546499999",
            "estado": "ERROR"
        },
        {
            "clave": "celular_2",
            "cel": "5493546401198",
            "estado": "OK"
        }
    ],
    "errores": 1
}
try:
    data = json.dumps(fields)#urllib.parse.urlencode(fields)
    
    r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/m-masivos", validate_certificate=False, headers=headers, data=data)
except Exception as e:
    if bot.SHOW_ERRORS:
        print("Error confirmando masivo")
        print("     Detalle: ")
        print(e)
        print(repr(e))
        print(e.args)
    r = e

if type(r) != urlfetch.UrlfetchException:
    if bot.SHOW_API_RESPONSES:
        print("API post_response: " + str(r.status_code))
        print("Data:")
        print(f"     {fields}")
        print("Response: " + str(r.content))

    if r.status_code != 200:
        if bot.SHOW_ERRORS:
            print("Error confirmando masivo")
            print("  Detalle: ")
            print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
        

