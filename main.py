# Packages
import sys, json, time
from datetime import datetime, timedelta

# Webdriver
from selenium import webdriver

# Application
import bot, actions

def start():
    # Obtener selectores
    with open('selectores.json', 'rb') as selectors:
        selectors = json.load(selectors)
    # Obtener MIME types

    # Abrir WhatsApp
    print("Intentando abrir navegador")
    done = driver = None
    while not done:
        if bot.BROWSER == 'chrome':
            driver = driver_connect_chrome("https://web.whatsapp.com")
            if driver:
                done = True
            else:
                print("Falló abrir navegador, reintentando...")
                time.sleep(5)
    
    driver.execute_script(f"document.title = 'CHATTER {bot.PHONE}'")

    # Sincronización
    sync(driver, selectors)
    
    # Registrar inicio
    bot.START_DATE = datetime.now()

    # Proximo reload
    bot.NEXT_FORCED_ACTIVITY = bot.START_DATE
    print("Próxima actividad forzada: ", str(bot.NEXT_FORCED_ACTIVITY))

    # Loop principal
    while True:
        driver.execute_script(f"document.title = 'CHATTER {bot.PHONE}'")

        # Revisar desincronización
        sync_needed = None
        try:
            driver.find_element_by_xpath(selectors["qr"])
            sync_needed = True
        except:
            try:
                driver.find_element_by_xpath(selectors["search"])
            except:
                sync_needed = True

        if sync_needed:    
            sync(driver, selectors)
        else:
            time.sleep(5)

        # Actividad forzada
        if datetime.now() >= bot.NEXT_FORCED_ACTIVITY:
            send_groups(driver, selectors)

            bot.NEXT_FORCED_ACTIVITY = datetime.now() + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY)
            print("Próxima actividad forzada: ", str(bot.NEXT_FORCED_ACTIVITY))
        
# Funciones de inicio  
def driver_connect_chrome(url=""):
    options = webdriver.chrome.options.Options()
    options.add_argument("--window-size=950,700")
    driver = webdriver.Chrome(executable_path=bot.DRIVER_PATH, chrome_options=options)

    try:
        driver.get(url)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error abriendo WhatsApp")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        driver = None

    return driver

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
    bot.MESSAGE = f"Hola! Soy chatter _*{bot.PHONE}*_"
    
    print(f'PHONE: {bot.PHONE}')

    bot.calc_sleeptime()

    for selector in selectors["back_button"]:
        try:
            driver.find_element_by_xpath(selector).click()
            break
        except:pass

# Managers
def send_groups(driver, selectors):
    actions.release_clipboard()
    for group in bot.GROUPS_LIST: # Enviar mensaje a los grupos
        actions.send_message(
            mensaje=bot.MESSAGE, 
            celular=group, 
            driver=driver, 
            selectors=selectors
        )

        print("Esperando 1min para el siguiente envío")
        time.sleep(60)
