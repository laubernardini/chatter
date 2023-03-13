# Packages
import sys, json, time, urlfetch
from datetime import datetime, timedelta

# Webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Application
import bot, actions

def start():
    # Obtener selectores
    with open('selectores.json', 'rb') as selectors:
        selectors = json.load(selectors)
        
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
    send_status("SINCRONIZADO")

    # Obtener configuraciones
    if bot.GROUPS_ONLY:
        with open('config.json', 'rb') as config:
            config = json.load(config)
        bot.GROUPS_LIST = config["groupsList"]
    else:
        bot.PHONES_LIST = get_phones_list()
    
    # Registrar inicio
    bot.START_DATE = bot.NEXT_FORCED_ACTIVITY = bot.NEXT_SEND = datetime.now()

    # Proximo reload
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
            send_status("BLOQUEADO")
            bot.PHONE = ""
            sync(driver, selectors)
        else:
            time.sleep(5)

        # Revisar notificaciones
        inbound_handler(driver, selectors)

        # Enviar
        set_next_forced_activity = send_handler(driver, selectors)

        # Actividad forzada
        if set_next_forced_activity:
            bot.NEXT_FORCED_ACTIVITY = bot.NEXT_SEND = datetime.now() + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY)
            print("Próxima actividad forzada: ", str(bot.NEXT_FORCED_ACTIVITY))
            if not bot.GROUPS_ONLY:
                bot.PHONES_LIST = get_phones_list()

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
    bot.set_message()
    
    print(f'PHONE: {bot.PHONE}')

    bot.calc_sleeptime()

    for selector in selectors["back_button"]:
        try:
            driver.find_element_by_xpath(selector).click()
            break
        except:pass

# Handlers
def send_handler(driver, selectors):
    actions.release_clipboard()
    set_next_activity = False

    # Enviar
    if datetime.now() >= bot.NEXT_SEND:
        list_for_send = bot.GROUPS_LIST if bot.GROUPS_ONLY else bot.PHONES_LIST
        if not bot.LAST_SEND:
            item = list_for_send[0]
        else:
            last_send_idx = list_for_send.index(bot.LAST_SEND)
            item = list_for_send[last_send_idx + 1] if last_send_idx < len(list_for_send) -1 else None

        if item:
            send(driver, selectors, item, is_groups=bot.GROUPS_ONLY)
            bot.LAST_SEND = item
            bot.NEXT_SEND = datetime.now() + timedelta(minutes=bot.AWAIT_TIME)
        else:
            set_next_activity = True
            bot.LAST_SEND = None
    else:
        print(f"Sin mensajes para enviar, próximo: {bot.NEXT_SEND}")
    
    return set_next_activity

def send(driver, selectors, item, is_groups=True):
    error = False
    
    result = actions.send_message(
        mensaje=bot.MESSAGE, 
        celular=item, 
        driver=driver, 
        selectors=selectors,
        init=not(is_groups)
    )
    if result == 'ERROR':
        error = True
    
    return error

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