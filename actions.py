import sys, os, shutil, re, time, asyncio

import bot, apis
from datetime import datetime, timedelta

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Acciones

# Manejo de chats
def get_chat_by_chat_name(chat_name): # Usar 'celular' UNICAMENTE
    chat = None
    for c in bot.CHATS:
        try:
            cel = None
            if '+' in chat_name:
                cel = cel_formatter(chat_name) 
            if c["celular"] == (cel if cel else chat_name):
                chat = c
                break
        except:
            pass
    
    return chat
  
def cel_formatter(celular): # Formatear celular
    chars_to_delete = [' ', '+', '-', '(', ')']
    for c in chars_to_delete:
        celular = celular.replace(c, '')

    return celular

def create_chat_by_data(nombre, celular, last_msg):
    new_chat = {
        "nombre": nombre,
        "celular": cel_formatter(celular),
        "last_msg": last_msg
    }

    # Guardar chat
    bot.CHATS.append(new_chat)

    return get_chat_by_chat_name(new_chat["celular"]) 

def get_data_by_chat_info(driver, selectors):
    # Navegar a la info del contacto
    driver.find_element_by_xpath(selectors["chat_name"]).click()
    time.sleep(2)
    info = driver.find_elements_by_xpath(selectors["chat_info"])
    
    # Obtener tipo
    try:
        if ('empresa' in driver.find_element_by_xpath(selectors["business_alert"]).text) or ('business' in driver.find_element_by_xpath(selectors["business_alert"]).text):
            tipo = 'business'
    except:
        tipo = 'common'
    print(f"Tipo de chat: {tipo}")
    
    # Obtener celular y nombre
    if tipo == 'common':
        try:
            celular = driver.find_element_by_xpath(selectors["phone"]).text
        except:
            celular = driver.find_element_by_xpath(selectors["contact_name"]).text

        if '~' in celular:
            nombre = celular.replace('~', '')
            celular = driver.find_element_by_xpath(selectors["contact_name"]).text
        else:
            try:
                nombre = driver.find_element_by_xpath(selectors["contact_name"]).text
            except:
                nombre = celular
    else:
        for i in info:
            try:
                if "+" in i.text:
                    celular = i.text
                    break
            except:pass
        try:
            nombre = driver.find_element_by_xpath(selectors["business_name"]).text
        except:
            try:
                nombre = driver.find_element_by_xpath(selectors["agended_business_name"]).text
            except:
                nombre = celular

    result = {
        "nombre": nombre,
        "celular": cel_formatter(celular),
    }
    print(result)

    # Cerrar info del contacto
    driver.find_element_by_xpath(selectors["chat_info_close"]).click()

    return result

# Búsqueda
def clear_elem(driver, selectors, id):
    driver.find_element_by_xpath(selectors[id]).clear()
    driver.find_element_by_xpath(selectors[id]).send_keys(Keys.ESCAPE)

def search(driver, selectors, text):
    print("Buscando: ", text)
    # Obtener input de búsqueda
    result = None
    no_result = False
    side = driver.find_element_by_xpath(selectors["side"]) 
    elem = side.find_element_by_xpath(selectors["search"])
    
    # Buscar
    #elem.send_keys(text)
    driver.execute_script("arguments[0].innerText = `{}`".format(text), elem)
    elem.send_keys('.')
    elem.send_keys(Keys.BACKSPACE)
    time.sleep(2)

    done = None
    while not done:
        try:
            searching = driver.find_element_by_xpath(selectors["searching"])
            try:
                search_result = searching.find_element_by_xpath(selectors["search_result_text"]).text
                if 'No ' in search_result:
                    no_result = True
                    done = True
            except:
                pass
        except:
            done = True
    
    if not no_result:
        # Seleccionar la primera opción
        elem.send_keys(Keys.ARROW_DOWN)
        if driver.switch_to.active_element == elem: # Revisa si hubo resultados, sino devuelve None
            elem.send_keys(Keys.TAB) # Prueba con TAB en caso de que no funcione ARROW_DOWN
            if driver.switch_to.active_element.get_attribute('class') == selectors["chat_class"]:
                result = driver.switch_to.active_element
        else:
            result = driver.switch_to.active_element
    
    return result

def archive(driver, selectors, text):
    r = search(driver, selectors, text)
    if r:
        chat = driver.switch_to.active_element
        chat.send_keys(Keys.ARROW_RIGHT)
        time.sleep(1)
        try:
            driver.find_element_by_xpath(selectors["archive"]).click()
        except Exception as e:
            if bot.SHOW_ERRORS:
                print("El chat ya está archivado")
                print(e)
                print(repr(e))
                print(e.args)
            r.click()
            r.clear()
            return True
    else:
        if bot.SHOW_EX_PRINTS:
            print("No se encontro el contacto")
        clear_elem(driver, selectors, "search")
        return True

    clear_elem(driver, selectors, "search")

def get_inbound_file():
    loaded = None
    dpath = f'inbound_file_cache{bot.OS_SLASH}{str(bot.BOT_PK)}{bot.OS_SLASH}'
    archivo = None
    new_name = ""
    ext = ""
    while not loaded:
        try:
            for (_, _, filenames) in os.walk(dpath):
                for fn in filenames:
                    if f"{dpath}{fn}" not in bot.FILE_CACHE:
                        archivo = f"{dpath}{fn}"
                break

            if archivo:
                loaded = True
                if ('.crdownload' in archivo):
                    new_name = archivo.replace('.crdownload', '')
                    os.rename(archivo, new_name)
                    archivo = new_name
                print(f"Archivo: {archivo}")

                ext = os.path.splitext(archivo)[1]
                new_name = f"inbound_file_cache{bot.OS_SLASH}{str(bot.BOT_PK)}{bot.OS_SLASH}{str(bot.FILE_COUNTER)}{ext}"
                os.rename(archivo, new_name)

                bot.FILE_COUNTER = bot.FILE_COUNTER + 1
                archivo = new_name
                print(f"Nuevo nombre: {archivo}")

                bot.FILE_CACHE.append(archivo)
                if bot.SHOW_EX_PRINTS:
                    print("Archivo obtenido")
            else:
                time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(2)
    return archivo

def chat_init(driver, selectors, celular):
    clear_elem(driver, selectors, "search")

    # Verificar chat propio abierto
    done = None
    while not done:
        search(driver, selectors, bot.PHONE)
        clear_elem(driver, selectors, "search")
        try:
            chat_header = driver.find_element_by_xpath(selectors["chat_header"])
            try:
                chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header"])
            except:
                chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header_1"])
                
            if bot.PHONE == cel_formatter(chat_name_header.text):
                done = True
        except:
            pass
        time.sleep(1)

    # Instanciar input mensaje
    done = None
    while not done:
        try:
            own_chat_message = driver.find_element_by_xpath(selectors["message"])
            done = True
        except:
            time.sleep(1)
    
    time.sleep(1)
    own_chat_message.send_keys("https://wa.me/" + celular)
    own_chat_message.send_keys(Keys.ENTER)
    
    # Esperar link
    done = None
    while not done:
        try:
            driver.find_element_by_xpath("//a[@href='https://wa.me/" + celular + "']").click()
            done = True
        except:
            time.sleep(1)
    
    # Popup
    done = None
    while not done:
            try:
                driver.find_element_by_xpath(selectors["modal_backdrop"]).click()

                # Comprobar número inválido
                try:
                    driver.find_element_by_xpath(selectors["chat_init"])
                    if "inválido" in driver.find_element_by_xpath(selectors["modal_text"]).text:
                        driver.find_element_by_xpath(selectors["no_file_ok_button"]).click()
                        elem = None
                        done = True
                        print("Número inválido")
                except:
                    try:
                        if "inválido" in driver.find_element_by_xpath(selectors["modal_text"]).text:
                            driver.find_element_by_xpath(selectors["no_file_ok_button"]).click()
                            elem = None
                            done = True
                            print("Número inválido")
                    except:
                        pass
            except:
                elem = True
                done = True
                print("Nuevo chat iniciado")
            time.sleep(1)
    

    return elem

def send_message(mensaje="", archivo="", celular="", masive=False, last_msg=None, driver=None, selectors=None):
    try:
        # Obtener chat si es respuesta manual
        if not masive:
            elem = search(driver, selectors, celular)
        else:
            elem = None

        # Iniciar chat
        if not elem:
            elem = chat_init(driver, selectors, celular)
        else:
            time.sleep(2)
        
        # Descartar cruce de chat
        if elem:
            try:
                chat_header = driver.find_element_by_xpath(selectors["chat_header"])
                try:
                    chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header"])
                except:
                    chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header_1"])
                print('Chat name: ', chat_name_header.text)
                if bot.PHONE == cel_formatter(chat_name_header.text):
                    elem = None
            except:
                elem = None

        # Enviar mensaje
        if elem:
            # Abrir chat (si es un chat vacío)
            try:
                elem.send_keys(Keys.ENTER)
            except:
                pass

            clear_elem(driver, selectors, "search")

            # Actualizar chat en ejecución
            update_current_chat(driver, selectors, celular=celular, last_msg=last_msg)

            # Obtener input de mensaje
            done = None
            while not done:
                try:
                    message = driver.find_element_by_xpath(selectors["message"])
                    done = True
                except:
                    time.sleep(1)
            #print("Conversación lista")

            # Revisar mensajes nuevos en el chat
            check_current_chat(driver=driver, selectors=selectors, chat=bot.CURRENT_CHAT)
            #print("Mensajes pendientes listos")

            # Preparar mensaje, reemplazar saltos de linea por caracter no utilizado -> `
            #mensaje = mensaje.replace("-#", '').replace("#-", '').replace("-*", "*").replace("*-", "*").replace("-_", "_").replace("_-", "_")#.replace("\r\n", "`").replace("\n\r", "`").replace("\n", "`").replace("\r", "`")
            #print("Mensaje preparado")

            attach_type = None
            if archivo:
                # Resolver tipo de archivo
                attach_type = 'doc'
                for ext in bot.MULTIMEDIA_EXT:
                    if ext in archivo:
                        attach_type = 'multimedia'
                
                # Descargar archivo temporalmente y obtener path
                try:
                    # Obtener archivo si ya ha sido descargado
                    f = open('file_cache' + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH + archivo)
                    file_path = os.path.abspath('file_cache' + bot.OS_SLASH + archivo)
                except:
                    file_path = apis.get_file(archivo)

                # Click en "Adjuntar"
                driver.find_element_by_xpath(selectors["attachments"]).click()
                time.sleep(1)

                # Obtener input para adjuntar correspondiente al tipo de archivo
                if attach_type == 'multimedia':
                    attach = driver.find_element_by_xpath(selectors["attach_multimedia"])
                else:
                    attach = driver.find_element_by_xpath(selectors["attach_file"])
                
                # Enviar path del archivo temporal
                attach.send_keys(file_path)
                time.sleep(1)

                # Actualizar elementos html para adjuntar
                driver.find_element_by_xpath(selectors["search"]).click()

                #driver.find_element_by_xpath(selectors["preview"]).click()
                
                send_file = False
                if attach_type == 'multimedia':
                    if masive or len(mensaje) < 1000:
                        # Obtener input de mensaje
                        e = None
                        while not e:
                            try:
                                message = driver.find_element_by_xpath(selectors["message_attached"])
                                e = True
                            except:
                                time.sleep(1)
                                driver.find_element_by_xpath(selectors["search"]).click()
                    else:
                        send_file = True
                else:
                    send_file = True
                
                if send_file:
                    # Enviar archivo
                    e = None
                    while not e:
                        try:
                            driver.find_element_by_xpath(selectors["file_submit"]).click()
                            e = True
                        except:
                            time.sleep(1)

            # Escribir mensaje
            driver.execute_script("let txt = arguments[0].innerText; arguments[0].innerText = txt + `{}`".format(mensaje), message)
            message.send_keys('.')
            message.send_keys(Keys.BACKSPACE)

            # Enviar mensaje
            message.send_keys(Keys.ENTER)
            time.sleep(2)
            #print("Mensaje enviado")

            # Revisar si hay algún mensaje sin leer
            try:
                if driver.find_elements_by_css_selector(selectors["message_in_container"])[-1].get_attribute("data-id") != bot.CURRENT_CHAT["last_msg"]:
                    # Revisar en el chat
                    check_current_chat(driver, selectors, chat=bot.CURRENT_CHAT)
            except:
                pass
            #print("Revisando pendientes")
            # Archivar el chat
            #archive(driver, selectors, celular)
            
            if bot.SHOW_EX_PRINTS:
                print("Buscando wa_id de mensaje enviado")
            last_send = driver.find_elements_by_css_selector(selectors["message_out_container"])[-1]
            done = None
            while not done:
                if last_send.get_attribute("data-id"):
                    wa_id = last_send.get_attribute("data-id")
                    done = True
                else:
                    time.sleep(1)
            
            result = {
                "estado": "ENVIADO", 
                "wa_id": wa_id
            }

            # Actualizar último mensaje del chat
            bot.CHATS[bot.CHATS.index(bot.CURRENT_CHAT)]["last_msg"] = wa_id

            bot.CURRENT_CHAT["last_msg"] = wa_id
            
            return result
        else:
            if bot.SHOW_ERRORS:
                print("Chat no encontrado")
            clear_elem(driver, selectors, "search")
            result = {
                "estado": "ERROR", 
                "wa_id": None
            }
            return result
    except Exception as e:
        if bot.SHOW_ERRORS:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Error enviando mensaje")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
            print(os.path.split(exc_tb.tb_frame.f_code.co_filename)[1], ", linea ", exc_tb.tb_lineno)
        result = {
            "estado": "ERROR", 
            "wa_id": None
        }
        return result

def update_current_chat(driver, selectors, last_msg=None, celular=None):
    print("Actualizando chat")
    if not celular:
        chat_info = get_data_by_chat_info(driver, selectors)
    else:
        chat_info = {
            "nombre": celular,
            "celular": celular
        }
    
    print(f"Chat info: {chat_info}")

    chat = get_chat_by_chat_name(chat_info["celular"])
    if not chat:
        # Pedir último mensaje
        if not last_msg:
            last_msg = apis.get_last_msg(celular=chat_info["celular"])

        chat = create_chat_by_data(nombre=chat_info["nombre"], celular=chat_info["celular"], last_msg=last_msg)
    
    # Indicar chat en ejecución
    bot.CURRENT_CHAT = get_chat_by_chat_name(chat["celular"])
    print(f"Chat actualizado, celular: {bot.CURRENT_CHAT['celular']}")

def notification_clicker(driver, selectors):
    done = None
    try:
        notifications = driver.find_elements_by_xpath(selectors["notification"])
        for n in notifications:
            if n.get_attribute("aria-label") == None:
                parent = n.find_element_by_xpath('.//..//..//..//..')

                # Si es chat de grupo o chat propio, continuar con la siguiente notificación
                is_own_chat = False
                is_group = False

                try:
                    conversation_name = parent.find_element_by_xpath(selectors["conversation_name"]).text
                    print(f'Conversación: {conversation_name}, BOT PHONE: {bot.PHONE}')
                    if cel_formatter(conversation_name) == bot.PHONE:
                        is_own_chat = True
                except:pass

                if not is_own_chat:    
                    try:
                        parent.find_element_by_xpath(selectors["sender_name"])
                        is_group = True
                    except:
                        try:
                            writing = parent.find_element_by_xpath(selectors["writing"])
                            if ' escribiendo' in (writing.get_attribute("title")) or ' typing' in (writing.get_attribute("title")):
                                is_group = True
                        except:
                            try:
                                done_1 = None
                                while not done_1:
                                    try:
                                        event = parent.find_element_by_xpath(selectors["group_event"])
                                        e_title = event.get_attribute("title")
                                        if e_title != '':
                                            if (' unió a' in e_title) or (' añadió a' in e_title) or (' salió del grupo' in e_title):
                                                is_group = True
                                            done_1 = True
                                    except:
                                        pass
                            except:
                                pass

                if is_group or is_own_chat:
                    continue
                
                # Ingresar al chat
                bot.CURRENT_CHAT = {}
                parent.click()

                time.sleep(2)
                done = True
                if done:
                    break

    except Exception as e:
        print(e)
        if bot.SHOW_EX_PRINTS:
            print("No hay notificaciones")
            
    return done

def check_current_chat(driver, selectors, chat=None): # Obtener y subir mensajes nuevos
    try:
        messages = []
        chat_name = ''

        # Comprobar chat abierto
        driver.find_element_by_xpath(selectors["message"])

        # Obtener nombre del chat
        try:
            chat_header = driver.find_element_by_xpath(selectors["chat_header"])
            try:
                chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header"])
            except:
                chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header_1"])
            chat_name = cel_formatter(chat_name_header.text)
            print('Chat name: ', chat_name)
        except:pass

        if chat_name != bot.PHONE:
            if bot.SHOW_EX_PRINTS:
                print("Buscando mensajes nuevos")
            
            # Definir sobre qué chat se trabaja
            print(f"Chequeando chat: {chat}")
            
            if chat:
                chat_changed = False
                if chat["celular"] != chat_name:
                    chat_changed = True

                if chat_changed:
                    print("Cambio de chat detectado")
                    update_current_chat(driver, selectors)
            else:
                update_current_chat(driver, selectors)

            if bot.CURRENT_CHAT["celular"] != bot.PHONE:
                # Obtener id's de mensajes nuevos
                try:
                    messages = get_inbounds(driver, selectors)
                except Exception as e:
                    if bot.SHOW_ERRORS:
                        print("Error al obtener mensajes nuevos")
                        print(e)
            else:
                print('Chat propio detectado')
        else:
            print('Chat propio detectado')

        # Formatear y subir mensajes
        if messages != []:
            try:
                messages = make_inbound_messages(driver, selectors, messages)
                if bot.SHOW_EX_PRINTS:
                    print("Subiendo mensajes nuevos")
                
                asyncio.run(apis.send_inbounds(messages))
            except Exception as e:
                if bot.SHOW_ERRORS:
                    print("Error al obtener mensajes nuevos")
                    print(e)
        else:
            if bot.SHOW_EX_PRINTS:
                print("No hay mensajes nuevos en este chat")
    except:
        if bot.SHOW_EX_PRINTS:
            print("No hay chat abierto")

def get_inbounds(driver, selectors):
    messages = []
    try:
        done = None
        first_msg = None
        reference_elem = None
        has_data_id = None

        # Localizar elemento de mensaje
        try:
            reference_elem = driver.find_element_by_xpath('//div[@data-id="' + bot.CURRENT_CHAT["last_msg"] + '"]')
            reference_elem.send_keys(Keys.ARROW_DOWN)
            reference_elem = driver.switch_to.active_element

            if selectors["chat_separator_class"] in reference_elem.get_attribute("class"):
                reference_elem = driver.find_elements_by_xpath(selectors["missed_call_container"])[-1]
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element
            if selectors["message_out_class"] in driver.switch_to.active_element.get_attribute("class"):
                reference_elem = driver.find_elements_by_css_selector(selectors["message_out_container"])[-1]
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element
            if bot.SHOW_EX_PRINTS:
                print("Mensaje en caché ", bot.CURRENT_CHAT["last_msg"])
        except:
            try:
                reference_elem = driver.find_element_by_xpath(selectors["unread"])
                reference_elem.click()
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element
                if bot.SHOW_EX_PRINTS:
                    print("Hay mensajes no leidos")
            except:
                try:
                    reference_elem = driver.find_elements_by_css_selector(selectors["message_out_container"])[-1]
                    reference_elem.send_keys(Keys.ARROW_DOWN)
                    reference_elem = driver.switch_to.active_element
                    if bot.SHOW_EX_PRINTS:
                        print("Navegando a primer mensaje desde ultimo mensaje saliente")
                except:
                    try:
                        first_msg = driver.find_elements_by_css_selector(selectors["message_in_container"])[0]
                        if bot.SHOW_EX_PRINTS:
                            print("Obteniendo primer mensaje entrante del chat")
                    except:
                        try:
                            first_msg = driver.find_elements_by_xpath(selectors["missed_call_container"])[-1]
                            if bot.SHOW_EX_PRINTS:
                                print("Obteniendo llamada perdida")
                        except:
                            done = True
        
        if not first_msg and not done:
            first_msg = reference_elem

            # Comprobar si es el mensaje de "este chat está cifrado"
            try:
                first_msg.find_element_by_xpath(selectors["encrypted_chat"])[-1] 
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
            except:
                pass

            # Buscar primer mensaje
            while not first_msg.get_attribute("data-id"):
                print(first_msg.get_attribute("class"), first_msg.get_attribute("data-tab"))

                if bot.SHOW_EX_PRINTS:
                    print("Obteniendo primer mensaje")

                # Comprobar si es un elemento del chat
                if selectors["chat_item_class"] in first_msg.get_attribute("class") or selectors["unread_class"] in first_msg.get_attribute("class"):
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                else:
                    first_msg.send_keys(Keys.TAB)
                    first_msg = driver.switch_to.active_element
                    time.sleep(0.5)
                
                # Comprobar si es el mensaje de "este chat está cifrado"
                try:
                    first_msg.find_element_by_xpath(selectors["encrypted_chat"])
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                except:
                    pass
        
        print("Mensaje obtenido")
        print(f"Primer mensaje: {first_msg.get_attribute('data-id')}")

        # Condiciones
        different_data_id = (first_msg.get_attribute("data-id") != bot.CURRENT_CHAT["last_msg"])
        not_msg_out = not(selectors["message_out_class"] in first_msg.get_attribute('class'))

        print(f"Es un mensaje nuevo: {different_data_id and not_msg_out}")

        # Guardando primer mensaje
        if different_data_id and not_msg_out:
            messages.append(first_msg.get_attribute("data-id"))
            last_msg = first_msg
        else:
            done = True

        # Obtener todos los mensajes nuevos
        while not done:
            try:
                last_msg.send_keys(Keys.ARROW_DOWN)
                next_msg = driver.switch_to.active_element
                if last_msg != next_msg:
                    # Condiciones
                    not_msg_out = not(selectors["message_out_class"] in next_msg.get_attribute('class'))
                    has_data_id = next_msg.get_attribute("data-id")

                    if not_msg_out and has_data_id:
                        messages.append(next_msg.get_attribute("data-id"))
                    
                    last_msg = next_msg
                else:
                    done = True
            except:
                done = True

    except:
        if bot.SHOW_EX_PRINTS:
            print("No hay mensajes no leidos")
    
    return messages

def make_inbound_messages(driver, selectors, messages):
    time.sleep(1)
    result = []
    print(messages)
    for m in messages:
        wa_id = m
        nombre = ""
        done = None

        # Instanciar mensaje
        while not done:
            try:
                m = driver.find_element_by_xpath('//div[@data-id="' + wa_id + '"]')
                done = True
            except:
                driver.find_element_by_xpath(selectors["message"]).click()
                time.sleep(0.8)

        # Variables de ejecución
        nombre = bot.CURRENT_CHAT["nombre"]
        celular = bot.CURRENT_CHAT["celular"]
        in_response = {}

        archivo = ""
        is_audio = False
        is_image = False
        is_video = False
        is_call = False
        is_link = False
        
        # Revisar si es llamada perdida
        try:
            m.find_element_by_xpath(selectors["missed_call"])
            is_call = True
        except:
            try:
                m.find_element_by_xpath(selectors["missed_video_call"])
                is_call = True
            except:
                pass
        
        if not is_call:
            # Buscar archivo
            try:
                try:
                    m.find_element_by_xpath(selectors["audio_icon"])
                except:
                    m.find_element_by_xpath(selectors["audio_status"])
                
                done = None
                while not done:
                    try:
                        m.find_element_by_xpath(selectors["audio_button"])
                        done = True
                    except:
                        try:
                            m.find_element_by_xpath(selectors["audio_loading"]).click()
                            if bot.SHOW_EX_PRINTS:
                                print("Forzando descarga de audio")
                            time.sleep(2)
                        except Exception as e:
                            print(e)
                            time.sleep(1)          
                
                is_audio = True
            except:
                try:
                    m.find_element_by_xpath(selectors["thumbnail"])
                    if not(selectors["attach_inbound_class"] in m.get_attribute('class')):
                        wait_time = datetime.now() + timedelta(seconds=10)
                        done = None
                        while not done:
                            if datetime.now() < wait_time:
                                if selectors["attach_inbound_class"] in m.get_attribute('class'):
                                    done = True
                                else:
                                    time.sleep(1)
                            else:
                                # Revisar si es que el archivo ya no está disponible
                                m.find_element_by_xpath(selectors["thumbnail"]).click()
                                time.sleep(2)
                                try:
                                    driver.find_element_by_xpath(selectors["no_file_ok_button"]).click()
                                    continue # Continuar con el siguiente elemento
                                except:
                                    driver.find_element_by_xpath(selectors["close_media"]).click()
                                    wait_time = datetime.now() + timedelta(seconds=10)
                    is_image = True
                except:
                    try:
                        try:
                            # Revisando si es un video a partir de un enlace
                            try:
                                html = m.find_element_by_xpath(selectors["message_text"]).get_attribute("innerHTML")
                            except:
                                html = m.find_element_by_xpath(selectors["message_text1"]).get_attribute("innerHTML")
                            if '<a' in html:
                                is_link = True
                        except:
                            pass
                        
                        if not is_link:
                            m.find_element_by_xpath(selectors["video_button"]).click()
                            is_video = True
                    except:
                        pass
            
            if is_image or is_audio:
                time.sleep(2)
                m.send_keys(Keys.ARROW_RIGHT)
                
                downl = None
                loaded = None

                while not loaded:
                    try:
                        downl = driver.find_element_by_xpath(selectors["download"])
                        loaded = True
                    except:
                        try:
                            m.find_element_by_xpath(selectors["message_checkbox"])
                            m.find_element_by_xpath(selectors["close_message_selection"]).click()
                            m.send_keys(Keys.ARROW_RIGHT)
                        except:
                            pass
                    time.sleep(1)
                
                if downl:
                    downl.click()

            elif is_video:
                done = None
                while not done:
                    if driver.find_element_by_xpath(selectors["download_media"]).get_attribute("aria-disabled") == 'false':
                        driver.find_element_by_xpath(selectors["download_media"]).click()
                        driver.find_element_by_xpath(selectors["close_media"]).click()
                        done = True
                    else:
                        time.sleep(2)

            elif selectors["attach_inbound_class"] in m.get_attribute("class"):
                try:
                    m.find_element_by_xpath(selectors["attach_inbound_download"]).click()
                except:
                    is_link = True

            if (is_video or is_audio or is_image or (selectors["attach_inbound_class"] in m.get_attribute("class"))) and not(is_link):
                if bot.SHOW_EX_PRINTS:
                    print("Descargando...")
                archivo = get_inbound_file()


            # Obtener texto
            try:
                try:
                    text = m.find_element_by_xpath(selectors["message_text"])
                except:
                    text = m.find_element_by_xpath(selectors["message_text1"])
                
                html = text.get_attribute("innerHTML")
                # Obtener emojis
                text = re.sub('<img.*?data-plain-text="','',html, flags=re.DOTALL)
                text = re.sub('" style.*?;"','',text, flags=re.DOTALL).replace('>', '')
                # Formatear negrita
                text = text.replace('<strong class="i0jNr selectable-text copyable-text" data-app-text-template="*${appText}*"', '*').replace('</strong', '*')
                # Formatear cursiva
                text = text.replace('<em class="i0jNr selectable-text copyable-text" data-app-text-template="_${appText}_"', '_').replace('</em', '_')
                # Eliminar link
                text = re.sub('<a.*?copyable-text"','',text, flags=re.DOTALL).replace('</a>', '')
                text = re.sub('<a.*?">','',text, flags=re.DOTALL).replace('</a>', '')
            except:
                try:
                    emojis = m.find_elements_by_xpath(selectors["emogi_container"])
                    text = ''
                    for ec in emojis:
                        text += ec.find_element_by_xpath(".//img").get_attribute("data-plain-text")
                except:
                    pass
            
            # Obtener contacto compartido
            try:
                m.find_element_by_xpath(selectors["shared_contact_button"]).click()
                time.sleep(2)
                shared_contact_name = ''
                shared_contact_phone = ''
                driver.find_element_by_xpath(selectors["modal_backdrop"]).click()
                try:
                    shared_contact_name = driver.find_element_by_xpath(selectors["shared_contact_name"]).text
                except Exception as e:
                    print(e)
                    try:
                        shared_contact_name = driver.find_element_by_xpath(selectors["shared_contact_name1"]).text
                    except Exception as e:
                        print(e)
                        pass

                try:
                    shared_contact_phone = driver.find_element_by_xpath(selectors["shared_contact_phone"]).text
                except Exception as e:
                    print(e)
                    try:
                        shared_contact_phone = driver.find_element_by_xpath(selectors["shared_contact_phone1"]).text
                    except Exception as e:
                        print(e)
                        pass

                m.find_element_by_xpath(selectors["chat_info_close"]).click()
                time.sleep(2)
                
                if shared_contact_phone != '': 
                    text = "*Contacto*\n_Nombre:_ " + shared_contact_name + "\n_Celular:_ " + shared_contact_phone
            except:pass

            text = " " if text == '' else text

            # Omitir mensaje vacío (eliminado)
            if archivo == '' and text == ' ':
                # Actualizar último mensaje del chat
                bot.CHATS[bot.CHATS.index(bot.CURRENT_CHAT)]["last_msg"] = wa_id

                bot.CURRENT_CHAT["last_msg"] = wa_id
                continue

            # Obtener 'en respuesta a...'
            try:
                # Obtener grupo
                group_elem = m.find_element_by_css_selector(selectors["in_response_group_class"])
                in_response_group = group_elem.find_element_by_xpath(".//span[1]").text.replace("Tú · ", "")

                # Obtener mensaje
                in_response_text = m.find_element_by_xpath(selectors["in_response_text"]).text

                in_response = {
                    "grupo": in_response_group,
                    "mensaje": in_response_text 
                }
            except:
                pass
        else:
            text = "*" + m.find_element_by_xpath(selectors["missed_call_text"]).text + "*"

            # Generar respuesta automática a llamada pedida
            bot.AUTO_RESPONSES.append({
                "celular": bot.CURRENT_CHAT["celular"],
                "mensaje": bot.CALL_RESPONSE, 
                "archivo": "",
                "tipo": "missed_call"
            })
        
        result.append({
            "wa_id": wa_id,
            "nombre": nombre,
            "celular": celular,
            "mensaje": text,
            "archivo": archivo,
            "respuesta": in_response
        })
        
        # Actualizar último mensaje del chat
        bot.CHATS[bot.CHATS.index(bot.CURRENT_CHAT)]["last_msg"] = wa_id

        bot.CURRENT_CHAT["last_msg"] = wa_id

    return result

def clear_cache():
    try:
        shutil.rmtree(f'inbound_file_cache{bot.OS_SLASH}{str(bot.BOT_PK)}{bot.OS_SLASH}')
        if bot.SHOW_EX_PRINTS:
            print("Caché limpiado")
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("El caché entrante no se puede limpiar/ya está limpio")

    try:
        shutil.rmtree(f'file_cache{bot.OS_SLASH}{str(bot.BOT_PK)}{bot.OS_SLASH}')
        if bot.SHOW_EX_PRINTS:
            print("Caché limpiado")
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("El caché saliente no se puede limpiar/ya está limpio")