# Packages
import os, sys, json, time
from datetime import datetime, timedelta

# Webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# Application
import bot, apis, actions

def start():
    actions.clear_cache()
    # Obtener selectores
    with open('selectores.json', 'rb') as selectors:
        selectors = json.load(selectors)
    # Obtener MIME types
    with open('mime_types.txt', 'rb') as mime:
        bot.MIME_TYPES = str(mime.read())

    # Abrir WhatsApp
    while bot.STATE != "OK":
        if bot.BROWSER == 'chrome':
            driver = driver_connect_chrome("https://web.whatsapp.com")#
        elif bot.BROWSER == 'firefox':
            driver = driver_connect_firefox("https://web.whatsapp.com")
        elif bot.BROWSER == 'opera':
            driver = driver_connect_opera("https://web.whatsapp.com")
    
    driver.execute_script(f"document.title = 'BOT {bot.BOT_PK}'")

    # Sincronización
    sync(driver, selectors)
    
    # Registrar inicio
    bot.START_DATE = datetime.now()

    # Proximo reload
    bot.NEXT_FORCED_ACTIVITY = bot.START_DATE + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY)
    print("Próxima actividad forzada: ", str(bot.NEXT_FORCED_ACTIVITY))

    # Loop principal
    while True:
        driver.execute_script(f"document.title = 'BOT {bot.BOT_PK}'")
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

        # Buscar desconexión de celular
        phone_disconected = False
        try:
            driver.find_element_by_xpath(selectors["phone_disconected"])
            phone_disconected = True
            if bot.SHOW_EX_PRINTS:
                print("Teléfono sin conexión, envíos en pausa")
        except:
            pass

        if not phone_disconected:
            # Outbounds
            if bot.STATE != 'ERROR':
                manage_response(driver=driver, selectors=selectors)
            
            # Masive
            if bot.STATE != 'ERROR':
                manage_masiv(driver=driver, selectors=selectors)
                time.sleep(1)
        else:
            time.sleep(3)
            
        # Limpiar caché
        #actions.clear_cache()

        # Actividad forzada
        if False:#datetime.now() >= bot.NEXT_FORCED_ACTIVITY:
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
def driver_connect_firefox(url=""):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", bot.DOWNLOAD_PATH)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.download.viewableInternally.enabledTypes", "")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", bot.MIME_TYPES)
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.closeWhenDone", False)
    profile.set_preference("browser.download.alwaysOpenPanel", False)
    profile.set_preference("pdfjs.disabled", True)
    #options = webdriver.firefox.options.Options()
    #options.headless = True
    driver = webdriver.Firefox(profile, executable_path=bot.FIREFOX_DRIVER_PATH)#, options=options)
    driver.set_window_position(0, 0)
    driver.set_window_size(800, 800)
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

def driver_connect_chrome(url=""):
    options = webdriver.chrome.options.Options()
    prefs = {
        "download.default_directory" : bot.DOWNLOAD_PATH,
        "download.prompt_for_download": False
    }
    options.add_experimental_option("prefs", prefs)

    if bot.VERSION == "3.0":
        options.add_argument("--window-size=950,700")

    driver = webdriver.Chrome(executable_path=bot.DRIVER_PATH, chrome_options=options)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': bot.DOWNLOAD_PATH}}
    driver.execute("send_command", params)

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

def driver_connect_opera(url=""):
    options = webdriver.chrome.options.Options()
    prefs = {
        "download.default_directory" : bot.DOWNLOAD_PATH,
        "download.prompt_for_download": False,
        "download.always_open_panel": False
    }
    options.add_experimental_option("prefs", prefs)

    if bot.VERSION == "3.0":
        options.add_argument("--window-size=950,700")

    driver = webdriver.Chrome(executable_path='operadriver.exe', chrome_options=options)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': bot.DOWNLOAD_PATH}}
    driver.execute("send_command", params)

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
    apis.status()
    if not bot.REGISTERED_PHONE or bot.REGISTERED_PHONE == '':
        raise_phone_error(error='registered')
    if bot.PHONE != '':
        if bot.REGISTERED_PHONE != 'ALL' and bot.REGISTERED_PHONE != bot.PHONE:
            raise_phone_error(error='phone')

def sync(driver, selectors):
    #if bot.SHOW_EX_PRINTS:
    print("\nWhatsApp abierto")
    waiting_qr = True
    waiting_wpp = False
    
    try:
        driver.find_element_by_xpath(selectors["search"])
        waiting_qr = False
    except:pass
    
    # Sincronización
    if waiting_qr:
        print("\nEsperando escaneo de QR")
        done = None
        while not done:
            try:
                driver.find_element_by_xpath(selectors["search"])
                waiting_qr = False
                print("\nQR Escaneado")
                done = True
            except:
                time.sleep(2)
                qr = None
                try:
                    qr = driver.find_element_by_xpath(selectors["qr"])
                except:pass
                if qr:
                    try:
                        qr.find_element_by_xpath(selectors["refresh_qr"]).click()
                        print("QR Refrescado")
                    except:pass
                else:
                    if not waiting_wpp:
                        waiting_wpp = True
                        print("\nEsperando a WhatsApp")
                
                sys.stdout.write(".")
                sys.stdout.flush()
            
    #if bot.SHOW_EX_PRINTS:
    print("\nSincronización completada!")
    send_report()

    # Buscar desconexión de celular
    phone_disconected = True
    while phone_disconected:
        try:
            driver.find_element_by_xpath(selectors["phone_disconected"])
            if bot.SHOW_EX_PRINTS:
                print("Teléfono sin conexión, envíos en pausa")
            time.sleep(1)
        except:
            phone_disconected = False

    time.sleep(2)
    if bot.PHONE == "":
        get_own_phone(driver, selectors)

    # Restablecer chats
    bot.CHATS = []
    bot.CURRENT_CHAT = {}

def get_own_phone(driver, selectors):
    time.sleep(3)
    print("Intentando entrar al perfil...")
    #profile_button = driver.find_element_by_xpath(selectors["main_header"]).find_element_by_xpath(".//div[@role='button']")
    #profile_button.click()
    profile = actions.get_parent(driver.find_element_by_xpath(selectors["profile_pic"]))
    done = None
    while not done:
        if profile.get_attribute("role") == 'button':
            profile.click()
            done = True
    
    time.sleep(3)
    done = None
    celular = None
    print("Buscando numero propio...")
    while not done:
        for selector in selectors["own_phone"]:
            try:
                celular = driver.find_element_by_xpath(selector).text
                break
            except:pass
        if celular:
            done = True
        else:
            time.sleep(1)
    bot.PHONE = actions.cel_formatter(celular)
    if bot.REGISTERED_PHONE != 'ALL' and bot.REGISTERED_PHONE != bot.PHONE:
        raise_phone_error(error='phone')
    print(f"PK: {bot.BOT_PK}, PHONE: {bot.PHONE}")

    for selector in selectors["back_button"]:
        try:
            driver.find_element_by_xpath(selector).click()
            break
        except:pass

def raise_phone_error(error):
    if error == 'phone':
        print(bot.INVALID_PHONE_MESSAGE)
    elif error == 'registered':
        print(bot.INVALID_REGISTERED_PHONE_MESSAGE)
    exit()

# Managers
def manage_response(driver, selectors):
    actions.release_clipboard()
    if bot.AUTO == "SI":
        # Respuestas automáticas
        for r in bot.AUTO_RESPONSES:
            actions.release_clipboard()
            if bot.SHOW_EX_PRINTS:
                print("Enviando respuesta automática: '", r.get("mensaje", ""), "'")
            
            result = actions.send_message(
                mensaje=r.get("mensaje", ""), 
                celular=actions.cel_formatter(r.get("celular", "")), 
                archivo=r.get("archivo", ""),
                driver=driver, 
                selectors=selectors
            )
            
            if result["estado"] != "ERROR":
                apis.post_auto_response(
                    mensaje=r.get("mensaje", "") if r.get("tipo", "") == "missed_call" else None, 
                    contacto_id=r.get("contacto_id", ""), 
                    celular=r.get("celular", ""), 
                    tipo=r.get("tipo", ""), 
                    wa_id=result.get("wa_id", ""), 
                    pk=r.get("pk", "")
                )

        bot.AUTO_RESPONSES = []
    if bot.RESPONDE == "SI":
        done = None
        counter = 5 # Para no enviar mas de 5 respuestas sin revisar entrantes
        while not done and counter > 0 and bot.RESPONDE == "SI":
            r = apis.get_response()
            actions.release_clipboard()
            if r:
                result = actions.send_message(
                    mensaje=r.get("mensaje", ""), 
                    celular=actions.cel_formatter(r.get("celular", "")), 
                    archivo=r.get("archivo", ""), 
                    last_msg=r.get("last_msg", ""),
                    driver=driver, 
                    selectors=selectors
                )

                apis.post_response(pk=r.get("pk", ""), estado=result["estado"], wa_id=result["wa_id"])
            else:
                if bot.SHOW_EX_PRINTS:
                    print("Sin respuestas pendientes")
                done = True
            counter -= 1

def manage_masiv(driver, selectors):
    if bot.MASIVO == 'SI':
        r = apis.get_masiv()
        actions.release_clipboard()
        if r:
            # Preparar mensaje masivo
            cel_list = r.get("celular", "{}")
            mensaje = r.get("mensaje", "")
            archivo = r.get("archivo", "")
            last_msg = r.get("last_msg", "")
            pk = r.get("pk", "")

            intentos = [] 
            errores = 0
            for clave, item in cel_list.items():
                result = actions.send_message(
                    mensaje=mensaje, 
                    celular=item["cel"], 
                    archivo=archivo,
                    last_msg=last_msg,
                    driver=driver, 
                    selectors=selectors,
                    masive=True,
                )
                intentos.append({
                    "clave": clave,
                    "cel": item["cel"],
                    "estado": ("ERROR" if result["estado"] == "ERROR" else "OK")
                })
                if result["estado"] == 'ENVIADO':
                    break
                else:
                    errores = errores + 1
            
            estado = ('ERROR' if result["estado"] == "ERROR" else 'FINALIZADO')
            wa_id = result["wa_id"]

            apis.post_masiv(pk=pk, wa_id=wa_id, estado=estado, intentos=intentos, errores=errores)
        else:
            if bot.SHOW_EX_PRINTS:
                print("Sin campañas pendientes")

def manage_inbounds(driver, selectors):
    if bot.READ == 'SI':
        # Revisar en el chat
        if bot.STATE != 'ERROR':
            chat_name_header = ''
            try:
                chat_header = driver.find_element_by_xpath(selectors["chat_header"])
                try:
                    chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header"]).text
                except:
                    chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header_1"]).text
            except:
                pass
            
            if actions.cel_formatter(chat_name_header) != bot.PHONE:
                if bot.SHOW_EX_PRINTS:
                    print("Revisando chat")
                actions.check_current_chat(driver, selectors, chat=bot.CURRENT_CHAT)

        # Obtener mensajes desde notificación
        if bot.STATE != 'ERROR':
            if bot.SHOW_EX_PRINTS:
                print("Buscando notificaciones")
            done = None
            while not done:
                n = actions.notification_clicker(driver, selectors)
                if n:
                    actions.check_current_chat(driver, selectors)

                    if bot.STATE == 'ERROR':
                        done = True
                    
                    time.sleep(1)
                else:
                    if bot.SHOW_EX_PRINTS:
                        print("No hay notificaciones")
                    done = True
        
        time.sleep(1)
