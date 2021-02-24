# Packages
import os, sys, json, time, asyncio
from datetime import datetime, timedelta

# Webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Application
import bot, apis, actions

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
    
    # Sincronización
    sync(driver, selectors)
    
    # Registrar inicio
    bot.START_DATE = datetime.now()

    # Proximo reload
    bot.NEXT_FORCED_ACTIVITY = bot.START_DATE + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY)
    print("Próxima actividad forzada: ", str(bot.NEXT_FORCED_ACTIVITY))

    # Loop principal
    while True:
        # Reporte de estado
        send_report()
        if bot.STATE == 'ERROR':
            # Revisar desincronización
            try:
                driver.find_element_by_xpath(selectors["qr"])
                sync(driver, selectors)
            except:
                try:
                    driver.find_element_by_xpath(selectors["search"])
                except:
                    sync(driver, selectors)

            time.sleep(2)
            bot.STATE = "OK"
            send_report()

        # Inbounds
        if bot.STATE != 'ERROR':
            manage_inbounds(driver, selectors)

        # Outbounds
        if (bot.RESPONDE == "SI" or bot.AUTO == "SI") and bot.STATE != 'ERROR':
            manage_response(driver=driver, selectors=selectors)
        
        # Masive
        if bot.MASIVO == "SI" and bot.STATE != 'ERROR':
            manage_masiv(driver=driver, selectors=selectors)
            time.sleep(1)
        
        # Limpiar caché
        actions.clear_cache()

        # Actividad forzada
        if datetime.now() >= bot.NEXT_FORCED_ACTIVITY:
            #if bot.SHOW_EX_PRINTS:
            print("Forzando actividad...")
            driver.refresh()

            # Sincronización
            sync(driver, selectors)

            # Actividad forzada
            #driver.find_element_by_xpath(selectors["search"]).click()

            bot.NEXT_FORCED_ACTIVITY = datetime.now() + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY)

            #if bot.SHOW_EX_PRINTS:
            print("Próxima actividad forzada: ", str(bot.NEXT_FORCED_ACTIVITY))

        # Check sync
        try:
            driver.find_element_by_xpath(selectors["search"])
        except:
            bot.STATE = "ERROR"
        
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

def send_report():
    asyncio.run(apis.status())

def sync(driver, selectors):
    #if bot.SHOW_EX_PRINTS:
    print("\nWhatsApp abierto")
    
    # Sincronización
    try:
        driver.find_element_by_xpath(selectors["search"])
        done = True
    except:
        print('\nEsperando escaneo de QR')
        done = None
    
    while not done:
        time.sleep(2)
        try:
            driver.find_element_by_xpath(selectors["qr"])
            sys.stdout.write(".")
            sys.stdout.flush()
        except:
            try:
                time.sleep(0.5)
                driver.find_element_by_xpath(selectors["refresh_qr"]).click()
            except:
                done = True
    
    print('\nEsperando a WhatsApp')

    done = None
    while not done:
        try:
            driver.find_element_by_xpath(selectors["search"])
            done = True
        except:
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(2)
    
    #if bot.SHOW_EX_PRINTS:
    print("\nSincronización completada!")
    send_report()

    # Restablecer chats
    bot.CHATS = []

# Managers
def manage_response(driver, selectors):
    if bot.AUTO == "SI":
        # Respuestas automáticas
        for r in bot.AUTO_RESPONSES:
            if bot.SHOW_EX_PRINTS:
                print("Enviando respuesta automática: '", r.get("mensaje", ""), "'")
            
            result = actions.send_message(
                mensaje=r.get("mensaje", ""), 
                celular=r.get("celular", ""), 
                archivo=r.get("archivo", ""),
                driver=driver, 
                selectors=selectors
            )
            
            if result["estado"] != "ERROR":
                asyncio.run(apis.post_auto_response(mensaje=r.get("mensaje", "") if r.get("tipo", "") == "missed_call" else None, celular=r.get("celular", ""), tipo=r.get("tipo", ""), wa_id=result.get("wa_id", ""), pk=r.get("pk", "")))

        bot.AUTO_RESPONSES = []
    if bot.RESPONDE == "SI":
        done = None
        counter = 5 # Para no enviar mas de 5 respuestas sin revisar entrantes
        while not done and counter > 0 and bot.RESPONDE == "SI":
            r = apis.get_response()
            if r:
                result = actions.send_message(
                    mensaje=r.get("mensaje", ""), 
                    celular=r.get("celular", ""), 
                    archivo=r.get("archivo", ""), 
                    last_msg=r.get("last_msg", ""),
                    driver=driver, 
                    selectors=selectors
                )
            
                asyncio.run(apis.post_response(pk=r.get("pk", ""), estado=result["estado"], wa_id=result["wa_id"]))
            else:
                if bot.SHOW_EX_PRINTS:
                    print("Sin respuestas pendientes")
                
                done = True
            counter -= 1

def manage_masiv(driver, selectors):
    r = apis.get_masiv()
    if r:
        chat = actions.get_chat_by_chat_name(r["celular"])
        if chat:
            bot.CURRENT_CHAT = chat
        else:
            bot.CURRENT_CHAT = actions.create_chat_by_data(nombre=r["celular"], celular=r["celular"], last_msg=None)

        # Preparar mensaje masivo
        mensaje = r.get("mensaje", "").replace("@apin", r.get("nombre", "")).replace("@apic", r.get("celular", "")).replace("@apivu", r.get("v_uni", ""))

        result = actions.send_message(
            mensaje=mensaje, 
            celular=r.get("celular", ""), 
            archivo=r.get("archivo", ""),
            last_msg=r.get("last_msg", ""),
            driver=driver, 
            selectors=selectors,
            masive=True,
        )
        asyncio.run(apis.post_masiv(pk=r.get("pk", ""), wa_id=r.get("wa_id", ""), estado=('ERROR' if result["estado"] == "ERROR" else 'FINALIZADO')))
    else:
        if bot.SHOW_EX_PRINTS:
            print("Sin campañas pendientes")

def manage_inbounds(driver, selectors):
    # Revisar en el chat
    if bot.STATE != 'ERROR':
        actions.check_current_chat(driver, selectors, chat=bot.CURRENT_CHAT)

    # Obtener mensajes desde notificación
    if bot.STATE != 'ERROR':
        done = None
        while not done:
            n = actions.notification_clicker(driver, selectors)
            if n:
                actions.check_current_chat(driver, selectors)

                if bot.STATE == 'ERROR':
                    done = True
                
                time.sleep(1)
            else:
                done = True
    
    time.sleep(1)
