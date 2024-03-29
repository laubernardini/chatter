# Packages
import sys, json, time, urlfetch
from datetime import datetime, timedelta

# Webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support.ui import WebDriverWait

import undetected_chromedriver as uc 

# Application
import bot, actions
from tools import *

def start():
    # Obtener selectores
    with open('selectores.json', 'rb') as selectors:
        selectors = json.load(selectors)
    bot.SELECTORS = selectors
        
    # Abrir WhatsApp
    print("Intentando abrir navegador")
    done = driver = None
    while not done:
        if bot.BROWSER == 'chrome':
            driver = driver_connect_undetected_chrome("https://web.whatsapp.com")
            if driver:
                done = True
            else:
                print("Falló abrir navegador, reintentando...")
                time.sleep(5)
    
    driver.execute_script(f"document.title = 'CHATTER {bot.PHONE}'")
    try:
        # Sincronización
        sync(driver, selectors)
        send_status("SINCRONIZADO")

        # Registrar inicio
        bot.START_DATE = datetime.now()

        # Obtener configuraciones
        if bot.GROUPS_ONLY:
            bot.GROUPS_LIST = get_groups_list()
            bot.NEXT_FORCED_ACTIVITY = bot.NEXT_SEND = bot.START_DATE
        else:
            #bot.PHONES_LIST = get_phones_list()
            bot.GROUPS_LIST = get_groups_list()
            bot.MODE_CHANGE = bot.START_DATE + timedelta(minutes=bot.MODE_CHANGE_TIME)
            bot.NEXT_FORCED_ACTIVITY = bot.START_DATE + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY * 2)
            if bot.MODE == 'REPLY':
                bot.NEXT_SEND = bot.NEXT_FORCED_ACTIVITY
            else:
                bot.NEXT_SEND = bot.START_DATE
        
        # Inicio de envios
        print("Inicio de envios: ", str(bot.NEXT_FORCED_ACTIVITY))

        # Loop principal
        while True:
            set_next_forced_activity = False
            driver.execute_script(f"document.title = 'CHATTER {bot.PHONE}'")

            # Revisar desincronización
            check_sync(driver, selectors)

            # Revisar notificaciones
            #inbound_handler(driver, selectors)

            # Enviar
            if bot.MODE == "GROUPS":
                set_next_forced_activity = send_handler(driver, selectors)
            else:
                group_read_handler(driver, selectors)
            # Actividad forzada
            if set_next_forced_activity:
                if bot.NEXT_SEND != bot.NEXT_FORCED_ACTIVITY:
                    bot.NEXT_FORCED_ACTIVITY = bot.NEXT_SEND = datetime.now() + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY)
                    print("Próxima actividad forzada: ", str(bot.NEXT_FORCED_ACTIVITY))
                #if not bot.GROUPS_ONLY:
                #    bot.PHONES_LIST = get_phones_list()
            
            # Cambio de modo
            if bot.MODE_CHANGE:
                print(f"Modo actual {bot.MODE}, próximo cambio: {bot.MODE_CHANGE}")
                if datetime.now() > bot.MODE_CHANGE:
                    if bot.MODE == "GROUPS":
                        bot.MODE = "REPLY"
                        bot.ACTUAL_READED_GROUP = ""
                        bot.ACTUAL_READED_MSG = ""
                    else:
                        bot.MODE = "GROUPS"
                    print(f"Cambiando modo a {bot.MODE}")
                    bot.NEXT_SEND = datetime.now()
                    bot.MODE_CHANGE = datetime.now() + timedelta(minutes=bot.MODE_CHANGE_TIME)
    except KeyboardInterrupt:
        print("cerrando navegador")
        driver.quit()

## Apis ##
# Prints
def print_api_response(content, name="", data=None, status_code=None):
    data_text = ""
    if data:
        data_text = "Data:"
        for key, value in data.items():
            data_text += f"\n    {key}={value}"

    print(f'''\nAPI {name} status: {status_code}\n{data_text}\nResponse: {content}''')

def print_api_status_error(where="", status_code=None, exception=None, detail=None):
    exception_text = ""
    status_code_text = ""

    if exception:
        exception_text = f'''Exception:
        {exception}
        {repr(exception)}
        {exception.args}
        '''
    if status_code:
        status_code_text = f'''Detalle:
        La petición tuvo un estado distinto a 200: {status_code}
        '''

    print(f'''Error {where}:\n{status_code_text}\n{exception_text}\n{f'Detalle: {detail}' if detail else ""}\n''')

def send_status(status):
    timeout = 15
    headers = {
        "Content-Type": "application/json"
    }
    fields = {
        "phone": bot.PHONE,
        "status": status,
        "descripcion": bot.DESCRIPCION
    }
    data=json.dumps(fields)
    
    done = None
    while not done:
        try:
            r = urlfetch.post(f'{bot.SERVER_URL}/api/bots/chatter', validate_certificate=False, data=data, headers=headers, timeout = timeout)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="send_inbound", data=fields, status_code=r.status_code)

            # Guardar respuesta automática
            if r.status_code == 200:
                content = json.loads(r.content)
                if content["request_status"] == 'success':
                    done = True
                    print("Estado registrado")
                else:
                    if bot.SHOW_ERRORS:
                        print_api_status_error(where="registrando estado")
                        print("Reintentando...")
                        time.sleep(3)
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="registrando estado", status_code=r.status_code)
                print("Reintentando...")
                time.sleep(3)
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="registrando estado", exception=e)
            print("Reintentando...")
            time.sleep(3)

def get_phones_list():
    print("Buscando lista de lineas...")

    result = None
    done = None
    while not done:
        try:
            r = urlfetch.get(f'{bot.SERVER_URL}/api/bots/chatter-lines?phone={bot.PHONE}', validate_certificate=False, timeout=15)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="get_phones_list", data={"phone": bot.PHONE}, status_code=r.status_code)
            
            if r.status_code == 200:
                content = json.loads(r.content)
                if content["request_status"] == 'success':
                    result = content.get("data", [])
                    done = True
                    print(f"Lista de lineas obtenidas: {len(result)} lineas")
                else:
                    if bot.SHOW_ERRORS:
                        print_api_status_error(where="obteniendo lista de lineas", detail=content["detail"])
                    bot.set_error()
                    time.sleep(3)
                    print("Reintentando...")
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="obteniendo lista de lineas", status_code=r.status_code)
                bot.set_error()
                time.sleep(3)
                print("Reintentando...")
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="obteniendo lista de lineas", exception=e)
            bot.set_error()    
            time.sleep(3)
            print("Reintentando...")    

    return result

def get_groups_list():
    with open('config.json', 'rb') as config:
        config = json.load(config)

    return config["groupsList"][bot.GROUPS_LIST_SOURCE]

def get_own_phone(driver, selectors):
    time.sleep(3)
    print("Intentando entrar al perfil...")
    
    profile = get_element(parent=driver, selector=selectors["profile_pic"])
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
        own_phone = get_element(parent=driver, selector=selectors["own_phone"])
        if own_phone:
            celular = own_phone.text
        if celular:
            done = True
        else:
            time.sleep(1)
    bot.PHONE = actions.cel_formatter(celular)
    bot.set_message()
    
    print(f'PHONE: {bot.PHONE}')

    bot.calc_sleeptime()

    click_element(parent=driver, selector=selectors["back_button"])

# Funciones de inicio  
def driver_connect_chrome(url=""):
    options = webdriver.chrome.options.Options()
    options.add_argument("--window-size=950,700")
    options.binary_location = bot.BINARY
    #options.add_argument("start-maximized")
    #options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(executable_path=bot.DRIVER_PATH, chrome_options=options)
    #driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    #driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    #print(driver.execute_script("return navigator.userAgent;"))
    
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

def driver_connect_undetected_chrome(url=""):
    options = uc.ChromeOptions()
    #size = f"9{bot.PHONE[-2:]},7{bot.PHONE[-2:]}"
    #print(size)
    #options.add_argument(f"--window-size={size}")
    options.binary_location = bot.BINARY
    driver = uc.Chrome(driver_executable_path=bot.DRIVER_PATH, options=options)

    try:
        driver.delete_all_cookies()
        delete_cache(driver)
        driver.get(url)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error abriendo WhatsApp")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        driver.quit()
        driver = None

    return driver

def sync(driver, selectors):
    #if bot.SHOW_EX_PRINTS:
    print("\nWhatsApp abierto")
    waiting_qr = True
    waiting_wpp = False

    if get_element(parent=driver, selector=selectors["search"]):
        waiting_qr = False
    
    # Sincronización
    if waiting_qr:
        print("\nEsperando escaneo de QR")
        done = None
        while not done:
            if get_element(parent=driver, selector=selectors["search"]):
                waiting_qr = False
                print("\nQR Escaneado")
                done = True
            else:
                time.sleep(2)
                qr = get_element(parent=driver, selector=selectors["qr"])
                if qr:
                    if click_element(parent=qr, selector=selectors["refresh_qr"]):
                        print("QR Refrescado")
                else:
                    if not waiting_wpp:
                        waiting_wpp = True
                        print("\nEsperando a WhatsApp")
                
                sys.stdout.write(".")
                sys.stdout.flush()
            
    #if bot.SHOW_EX_PRINTS:
    print("\nSincronización completada!")

    # Buscar desconexión de celular
    phone_disconected = False

    time.sleep(2)
    if bot.PHONE == "":
        get_own_phone(driver, selectors)

    # Restablecer chats
    bot.CHATS = []
    bot.CURRENT_CHAT = {}

def check_sync(driver, selectors):
    sync_needed = None
    if get_element(parent=driver, selector=selectors["qr"]):
        sync_needed = True
    else:
        if not get_element(parent=driver, selector=selectors["search"]):
            sync_needed = True

    if sync_needed:
        send_status("BLOQUEADO")
        bot.PHONE = ""
        sync(driver, selectors)
    else:
        time.sleep(5)

def delete_cache(driver):
    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
    #perform_actions(driver, (Keys.TAB * 3) + (Keys.DOWN * 4) + (Keys.TAB * 5))  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
    time.sleep(10)
    driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.

def perform_actions(driver, keys):
    actions = ActionChains(driver)
    actions.send_keys(keys)
    time.sleep(2)
    print('Performing Actions!')
    actions.perform()

# Handlers
def send_handler(driver, selectors):
    actions.release_clipboard()
    set_next_activity = False

    # Enviar
    if datetime.now() >= bot.NEXT_SEND:
        list_for_send = bot.GROUPS_LIST# if bot.GROUPS_ONLY else bot.PHONES_LIST
        if not bot.LAST_SEND:
            item = list_for_send[0]
        else:
            last_send_idx = list_for_send.index(bot.LAST_SEND)
            item = list_for_send[last_send_idx + 1] if last_send_idx < len(list_for_send) -1 else None

        if item:
            send(driver, selectors, item)
            bot.LAST_SEND = item
            bot.NEXT_SEND = datetime.now() + timedelta(minutes=bot.AWAIT_TIME if bot.MODE == "REPLY" else 1)
        else:
            set_next_activity = True
            bot.LAST_SEND = None
    else:
        print(f"Sin mensajes para enviar, próximo: {bot.NEXT_SEND}")
    
    return set_next_activity

def send(driver, selectors, item):
    error = False
    
    result = actions.send_message(
        mensaje=bot.MESSAGE, 
        celular=item, 
        driver=driver, 
        selectors=selectors,
        init=bot.MODE == 'REPLY'
    )
    if result == 'ERROR':
        error = True
    
    return error

def group_read_handler(driver, selectors):
    print("Revisando grupos")
    if bot.MODE == "REPLY" and bot.NEXT_SEND <= datetime.now():
        if bot.ACTUAL_READED_GROUP == "":
            bot.ACTUAL_READED_GROUP = bot.GROUPS_LIST[0]
        
        success = actions.read_chat(driver, selectors, bot.ACTUAL_READED_GROUP)

        if not success:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            bot.ACTUAL_READED_MSG = ""
            actual_group_idx = bot.GROUPS_LIST.index(bot.ACTUAL_READED_GROUP)
            if actual_group_idx >= 0:
                bot.ACTUAL_READED_GROUP = bot.GROUPS_LIST[actual_group_idx + 1] if actual_group_idx < len(bot.GROUPS_LIST) - 1 else bot.GROUPS_LIST[0]
            else:
                bot.ACTUAL_READED_GROUP = ""
        else:
            bot.NEXT_SEND = datetime.now() + timedelta(minutes=bot.AWAIT_TIME)
    else:
        print(f"Sin mensajes por responder, próximo: {bot.NEXT_SEND}")

def inbound_handler(driver, selectors):
    if not bot.GROUPS_ONLY:
        # Obtener mensajes desde notificación
        if bot.SHOW_EX_PRINTS:
            print("Buscando notificaciones")
        done = None
        while not done:
            n = actions.notification_clicker(driver, selectors)
            if n:
                actions.close_confirm_popup(driver, selectors)
                response = actions.get_inbounds(driver, selectors)
                # Cerrar chat
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                
                if response:
                    item = response.split('@')[0].replace('true_', '').replace('false_', '')
                    actions.send_message(
                        mensaje=f'{bot.RESPONSE_MSG} _*{item}*_ _(cttr)_', 
                        celular=item, 
                        driver=driver, 
                        selectors=selectors
                    )
                
                time.sleep(1)
            else:
                if bot.SHOW_EX_PRINTS:
                    print("No hay notificaciones")
                done = True
        
        time.sleep(1)