import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import json
import time
import asyncio
from datetime import datetime, timedelta

import bot 
import apis
import actions


def start():

    # Obtener selectores
    with open('selectores.json', 'rb') as selectors:
        selectors = json.load(selectors)
    # Obtener MIME types
    with open('mime_types.txt', 'rb') as mime:
        bot.MIME_TYPES = str(mime.read())

    # Abrir WhatsApp
    while bot.STATE != "OK":
        driver = driver_connect("https://web.whatsapp.com")
    if bot.SHOW_EX_PRINTS:
        print("WhatsApp abierto, esperando sincronización")
    
    # Sincronización
    sync(driver, selectors)
    
    # Registrar inicio
    bot.START_DATE = datetime.now()

    # Proximo reload
    bot.NEXT_RELOAD = bot.START_DATE + timedelta(minutes=bot.RELOAD_FRECUENCY)
    if bot.SHOW_EX_PRINTS:
        print("Próximo reload: ", str(bot.NEXT_RELOAD))

    # Loop principal
    while True:
        check_status()
        bot.STATE = "OK"
        manage_inbounds(driver, selectors)
        if bot.RESPONDE == "SI" or bot.AUTO == "SI":
            manage_response(driver=driver, selectors=selectors)
            time.sleep(1)
        if bot.MASIVO == "SI":
            manage_masiv(driver=driver, selectors=selectors)
            time.sleep(1)
        actions.clear_cache()
        manage_inbounds(driver, selectors)
        if datetime.now() >= bot.NEXT_RELOAD:
            #if bot.SHOW_EX_PRINTS:
            print("Recargando...")
            driver.refresh()

            # Sincronización
            sync(driver, selectors)

            bot.NEXT_RELOAD = datetime.now() + timedelta(minutes=bot.RELOAD_FRECUENCY)

            #if bot.SHOW_EX_PRINTS:
            print("Próximo reload: ", str(bot.NEXT_RELOAD))

# Funciones de inicio  
def driver_connect(url=""):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", bot.DOWNLOAD_PATH)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.download.viewableInternally.enabledTypes", "")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", bot.MIME_TYPES)
    profile.set_preference("pdfjs.disabled", True)
    #options = webdriver.firefox.options.Options()
    #options.headless = True
    driver = webdriver.Firefox(profile)#, options=options)
    try:
        driver.get(url)
        bot.STATE = "OK"
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error abriendo WhatsApp")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        bot.STATE = "ERROR"
        time.sleep(5)

    return driver

def check_status():
    asyncio.run(apis.status())

def sync(driver, selectors):
    #if bot.SHOW_EX_PRINTS:
    print("WhatsApp abierto, esperando sincronización")
    
    # Sincronización
    done = None
    while not done:
        try:
            driver.find_element_by_xpath(selectors["search"]).click()
            done = True
        except:
            time.sleep(2)
            # driver.save_screenshot("qr.png")
            if bot.SHOW_EX_PRINTS:
                print('.')
    
    #if bot.SHOW_EX_PRINTS:
    print("\nSincronizado!")

# Managers
def manage_response(driver, selectors):
    if bot.AUTO == "SI":
        for auto in bot.AUTO_RESPONSES:
            r = actions.send_message(
                mensaje=auto.get("mensaje", ""), 
                celular=auto.get("celular", ""), 
                archivo=auto.get("archivo", ""),
                driver=driver, 
                selectors=selectors
            )
            if r:
                archivo = r
            else:
                archivo = ""
            asyncio.run(apis.post_auto_response(celular=auto.get("celular", ""), mensaje=auto.get("mensaje", ""), archivo=archivo))
        bot.AUTO_RESPONSES = []
    if bot.RESPONDE == "SI":
        done = None
        counter = 5 # Para no enviar mas de 5 respuestas sin revisar entrantes
        while not done and counter > 0:
            response = apis.get_response()
            if response.get("pk", "") != "":
                r = actions.send_message(
                    mensaje=response.get("mensaje", ""), 
                    celular=response.get("celular", ""), 
                    archivo=response.get("archivo", ""),
                    driver=driver, 
                    selectors=selectors
                )
                asyncio.run(apis.post_response(response.get("pk", ""), estado=('ENVIADO' if not r else 'ERROR')))

                # Revisar entrantes
                actions.check_current_chat(driver, selectors)
            else:
                if bot.SHOW_EX_PRINTS:
                    print("Sin respuestas pendientes")
                done = True
            counter -= 1

def manage_masiv(driver, selectors):
    response = apis.get_masiv()
    if response.get("pk", "") != "":
        # Preparar mensaje masivo
        mensaje = response.get("mensaje", "").replace("@apin", response.get("nombre", "")).replace("@apic", response.get("celular", "")).replace("@apivu", response.get("v_uni", ""))

        r = actions.send_message(
            mensaje=mensaje, 
            celular=response.get("celular", ""), 
            archivo=response.get("archivo", ""),
            driver=driver, 
            selectors=selectors,
            masive=True,
        )
        asyncio.run(apis.post_masiv(pk=response.get("pk", ""), estado=('ERROR' if r == "ERROR" else 'FINALIZADO')))
    else:
        if bot.SHOW_EX_PRINTS:
            print("Sin campañas pendientes")

def manage_inbounds(driver, selectors):
    # Revisar en el chat
    actions.check_current_chat(driver, selectors)

    # Obtener mensajes desde notificación
    e = actions.notification_clicker(driver, selectors)
    if not e:
        actions.check_current_chat(driver, selectors)

    # Revisar si hay chats leidos sin abrir
    e = actions.readed_chat_clicker(driver, selectors)
    if not e:
        actions.check_current_chat(driver, selectors)
    
    # Revisar en el chat
    actions.check_current_chat(driver, selectors)





