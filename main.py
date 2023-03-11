# Packages
import sys, json, time, urlfetch
from datetime import datetime, timedelta

# Webdriver
from selenium import webdriver

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
            send_status("BLOQUEADO")
            bot.PHONE = ""
            sync(driver, selectors)
        else:
            time.sleep(5)

        # Actividad forzada
        if datetime.now() >= bot.NEXT_FORCED_ACTIVITY:
            error = send_handler(driver, selectors)
            if not error:
                bot.NEXT_FORCED_ACTIVITY = datetime.now() + timedelta(minutes=bot.FORCED_ACTIVITY_FREQUENCY)
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
    bot.MESSAGE = f"Hola! Soy chatter _*{bot.PHONE}*_ (_cttr_)"
    
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

    return send(driver, selectors, list_for_send=bot.GROUPS_LIST) if bot.GROUPS_ONLY else send(driver, selectors, list_for_send=bot.PHONES_LIST, is_groups=False)

def send(driver, selectors, list_for_send, is_groups=True):
    error = False
    counter = 0
    for item in list_for_send: # Enviar mensaje a los grupos
        if not is_groups:
            if counter > 0 and counter % bot.SERIES == 0:
                print(f"Pausa de {bot.FORCED_ACTIVITY_FREQUENCY}min")
                time.sleep(bot.FORCED_ACTIVITY_FREQUENCY * 60)

        result = actions.send_message(
            mensaje=bot.MESSAGE, 
            celular=item, 
            driver=driver, 
            selectors=selectors,
            group=is_groups
        )
        if result == 'ERROR':
            error = True
            break
        
        counter += 1
        print("Esperando 30sec para el siguiente envío")
        time.sleep(30)
    
    return error