import sys, os, shutil, re, time, pyperclip

import bot, apis
from datetime import datetime, timedelta

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Acciones

# Clipboard
def wait_and_set(text, clipboard_sleep_time):
    while not ":f:" in pyperclip.paste() or pyperclip.paste() == "":
        print(f"Esperando clipboard {clipboard_sleep_time} segundos")
        time.sleep(clipboard_sleep_time)
        release_clipboard()
    pyperclip.copy(text)

def release_clipboard():
    if f":{bot.BOT_PK}:" in pyperclip.paste() or pyperclip.paste() == '':
        pyperclip.copy(':f:')

def get_parent(element):
    return element.find_element_by_xpath('..')

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
    
    if celular.startswith('0'):
        celular = celular[1:]
    
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
    
    # Obtener tipo
    try:
        if ('empresa' in driver.find_element_by_xpath(selectors["business_alert"]).text) or ('business' in driver.find_element_by_xpath(selectors["business_alert"]).text):
            tipo = 'business'
        # Chat info items (para obtener celular)
        info = None
        for selector in selectors["chat_info"]:
            try:
                info = driver.find_elements_by_xpath(selector)
                break
            except:pass
    except:
        tipo = 'common'
    print(f"Tipo de chat: {tipo}")
    
    # Obtener celular y nombre
    celular = nombre = None
    if tipo == 'common':
        for selector in selectors["phone"]:
            try:
                celular = driver.find_element_by_xpath(selector).text
                break
            except:pass
        if not celular:
            for selector in selectors["contact_name"]:
                try:
                    celular = driver.find_element_by_xpath(selector).text
                    break
                except:pass

        if celular:
            if '~' in celular:
                nombre = celular.replace('~', '')
                for selector in selectors["contact_name"]:
                    try:
                        celular = driver.find_element_by_xpath(selector).text
                        break
                    except:pass
            else:
                for selector in selectors["contact_name"]:
                    try:
                        nombre = driver.find_element_by_xpath(selector).text
                        break
                    except:pass
                if not nombre:
                    nombre = celular
    else:
        for i in info:
            try:
                if "+" in i.text:
                    celular = i.text
                    break
            except:pass

        if not celular:
            for selector in selectors["agended_business_name"]:
                try:
                    if '+' in driver.find_element_by_xpath(selector).text:
                        celular = driver.find_element_by_xpath(selector).text
                        break
                except:pass

        for selector in selectors["agended_business_name"]:
            try:
                nombre = driver.find_element_by_xpath(selector).text
                break
            except:pass

        if not nombre:
            for selector in selectors["business_name"]:
                try:
                    nombre = driver.find_element_by_xpath(selector).text
                    break
                except:pass
   
        if not nombre:
            nombre = celular
    
    # Cerrar info del contacto
    for selector in selectors["chat_info_close"]:
        try:
            driver.find_element_by_xpath(selector).click()
            break
        except:pass

    if not celular:
        raise Exception(f"No se pudo encotrar celular ({tipo} contact)")

    result = {
        "nombre": nombre,
        "celular": cel_formatter(celular),
    }
    print(result)
    try:
        int(result["celular"])
    except:
        raise Exception(f"result['celular'] no es un número de téfono válido --> {result['celular']}")
    
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
                no_result = searching.find_element_by_xpath(selectors["no_chat_found"])
                no_result = True
                done = True
            except:pass
        except:
            done = True
    
    if not no_result:
        # Seleccionar la primera opción
        elem.send_keys(Keys.ARROW_DOWN)
        elem.send_keys(Keys.ENTER)
        if driver.switch_to.active_element == elem: # Revisa si hubo resultados, sino devuelve None
            elem.send_keys(Keys.TAB) # Prueba con TAB en caso de que no funcione ARROW_DOWN
            elem.send_keys(Keys.ENTER)
            if driver.switch_to.active_element.get_attribute('class') == selectors["chat_class"]:
                result = driver.switch_to.active_element
        else:
            result = driver.switch_to.active_element
    
    return result

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
                    if f"{dpath}{fn}" not in bot.FILE_CACHE and not fn.endswith(".crdownload"):
                        if f"{dpath}{fn}" == "downloads.htm":
                            try:
                                os.remove(f"{dpath}{fn}")
                            except:pass
                        else:
                            archivo = f"{dpath}{fn}"
                break

            if archivo:
                loaded = True
                #if ('.crdownload' in archivo):
                #    new_name = archivo.replace('.crdownload', '')
                #    os.rename(archivo, new_name)
                #    archivo = new_name
                #print(f"Archivo: {archivo}")

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
    
    time.sleep(2)
    try:
        driver.find_element_by_xpath("message1")
    except:pass
    
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
            try:
                own_chat_message = driver.find_element_by_xpath(selectors["message"])
            except:
                own_chat_message = driver.find_element_by_xpath(selectors["message1"])
            done = True
        except:
            time.sleep(1)
    
    time.sleep(1)
    link = f"https://wa.me/{celular}"
    for char in link:
        own_chat_message.send_keys(char)
    own_chat_message.send_keys(Keys.ENTER)
    
    # Esperar link
    done = None
    while not done:
        try:
            driver.find_element_by_xpath("//a[@href='https://wa.me/" + celular + "']").click()
            done = True
        except:
            time.sleep(2)
    
    # Popup
    done = None
    while not done:
        try:
            for selector in selectors["modal_backdrop"]:
                try:
                    driver.find_element_by_xpath(selector).click()
                except:pass
            
            loadig_confirm = False
            try:
                driver.find_element_by_xpath(selectors["modal_header"])
                driver.find_element_by_xpath(selectors["modal_header"]).click()
                loadig_confirm = True
            except:pass

            if not loadig_confirm:
                # Instanciar modal
                modal_elem_list = driver.find_elements_by_xpath(selectors["modal"])
                print(f"Modal elem: {len(modal_elem_list)}")
                modal = None
                for m in modal_elem_list:
                    print(f"Modal tabindex: {m.get_attribute('tabindex')}")
                    if not m.get_attribute("tabindex") or m.get_attribute("tabindex") != '-1':
                        modal = m
                        break
                
                print(f"Modal: {modal}")
                if not modal:
                    modal = modal_elem_list[-1]

                # Click en modal
                for selector in selectors["modal_body"]:
                    try:
                        modal.find_element_by_xpath(selector).click()
                    except:pass

                # Comprobar número inválido
                try:
                    modal.find_element_by_xpath(selectors["modal_header"])
                    if "inválido" in modal.find_element_by_xpath(selectors["modal_text"]).text:
                        modal.find_element_by_xpath(selectors["modal_ok_button"]).click()
                        elem = None
                        done = True
                        print("Número inválido")
                except:
                    try:
                        if "inválido" in modal.find_element_by_xpath(selectors["modal_text"]).text:
                            modal.find_element_by_xpath(selectors["modal_ok_button"]).click()
                            elem = None
                            done = True
                            print("Número inválido")
                    except:pass
        except:
            elem = True
            done = True
            print("Nuevo chat iniciado")
        time.sleep(1)
    
    return elem

def open_chat(driver, selectors, celular, masive=False, tipo='SALIENTE'):
    elem = None
    
    if not masive:
        elem = search(driver, selectors, celular)

    if tipo == 'SALIENTE':
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
            if tipo == 'SALIENTE':
                if bot.PHONE == cel_formatter(chat_name_header.text):
                    elem = None
        except:
            elem = None
    
    return elem

def send_message(mensaje="", archivo="", celular="", masive=False, last_msg=None, driver=None, selectors=None):
    try:
        elem = open_chat(driver, selectors, celular, masive)
        new_message_input = False

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
                    try:
                        message = driver.find_element_by_xpath(selectors["message"])
                    except:
                        message = driver.find_element_by_xpath(selectors["message1"])
                        new_message_input = True
                    done = True
                except:
                    time.sleep(1)
            print("Conversación lista")

            # Revisar mensajes nuevos en el chat
            check_current_chat(driver=driver, selectors=selectors, chat=bot.CURRENT_CHAT)
            print("Mensajes pendientes listos")
            
            time.sleep(2)
            attach_type = None
            if archivo:
                # Resolver tipo de archivo
                attach_type = 'doc'
                for ext in bot.MULTIMEDIA_EXT:
                    if ext in archivo:
                        attach_type = 'multimedia'
                        for ext in bot.AUDIO_EXT:
                            if ext in archivo:
                                attach_type = 'audio'

                
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
                if attach_type == 'multimedia' or attach_type == 'audio':
                    attach = driver.find_element_by_xpath(selectors["attach_multimedia"])
                else:
                    attach = driver.find_element_by_xpath(selectors["attach_file"])
                
                # Enviar path del archivo temporal
                attach.send_keys(file_path)
                time.sleep(1)
                print("Archivo cargado")

                # Actualizar elementos html para adjuntar
                driver.find_element_by_xpath(selectors["search"]).click()
               
                send_file = False
                if attach_type == 'multimedia':
                    if masive or len(mensaje) < 1000:
                        # Obtener input de mensaje
                        print("Obteniendo input de mensaje adjunto")
                        e = None
                        message = None
                        while not e:
                            for selector in selectors["message_attached"]:
                                try:
                                    message = driver.find_element_by_xpath(selector)
                                    break
                                except:pass
                            if message:
                                if message.get_attribute("data-lexical-editor") == "true":
                                    new_message_input = True
                                else:
                                    new_message_input = False
                                e = True
                            if not e:
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
                            get_parent(driver.find_element_by_xpath(selectors["send_button_icon"])).click()
                            e = True
                        except:
                            time.sleep(1)

            # Escribir mensaje
            if new_message_input:
                act = ActionChains(driver)
                act.click(message)

                # Manejo del clipboard
                text = mensaje.replace(':f:', "") + f':{bot.BOT_PK}:'
                while pyperclip.paste() != text:
                    print(f"Esperando {bot.SLEEP_TIME} segundos")
                    time.sleep(bot.SLEEP_TIME)
                    while not f":{bot.BOT_PK}:" in pyperclip.paste():
                        wait_and_set(text, bot.CLIPBOARD_SLEEP_TIME)
                
                # Pegar mensaje
                act.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
                time.sleep(0.5)

                # Limpiar código y liberar clipboard
                act.click(message)
                time.sleep(0.5)
                act.key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL)
                act.send_keys(Keys.BACKSPACE)
                for d in bot.BOT_PK:
                    act.send_keys(Keys.BACKSPACE)
                act.send_keys(Keys.BACKSPACE)
                act.perform()
                release_clipboard()
            else:
                driver.execute_script("let txt = arguments[0].innerText; arguments[0].innerText = txt + `{}`".format(mensaje), message)
                message.send_keys('.')
                message.send_keys(Keys.BACKSPACE)
            
            time.sleep(0.5)

            # Enviar mensaje
            message.send_keys(Keys.ENTER)
            time.sleep(2)
            print("Mensaje enviado")

            # Revisar si hay algún mensaje sin leer
            try:
                message_in_container = None
                for selector in selectors["message_in_container"]:
                    try:
                        message_in_container = driver.find_elements_by_css_selector(selector)[-1]
                        break
                    except:pass

                if message_in_container.get_attribute("data-id") != bot.CURRENT_CHAT["last_msg"]:
                    # Revisar en el chat
                    check_current_chat(driver, selectors, chat=bot.CURRENT_CHAT)
            except:
                pass
            #print("Revisando pendientes")
            # Archivar el chat

            if bot.SHOW_EX_PRINTS:
                print("Buscando wa_id de mensaje enviado, esperando 15s para ignorar...")
            
            done = None
            last_send = None
            sleep_counter = 0
            while (not done) and (sleep_counter < 15):
                try:
                    last_send = None
                    for selector in selectors["message_out_container"]:
                        try:
                            last_send = driver.find_elements_by_css_selector(selector)[-1]
                            break
                        except:pass
                    if last_send:
                        done = True
                    else:
                        int("s")
                except:
                    time.sleep(1)
                    sleep_counter = sleep_counter + 1
            
            if last_send:
                done = None
                while not done:
                    if last_send.get_attribute("data-id"):
                        wa_id = last_send.get_attribute("data-id")
                        done = True
                    else:
                        time.sleep(1)
            else:
                print('No se encontró "wa_id", ignorando')
                wa_id = "SD"
            
            result = {
                "estado": "ENVIADO", 
                "wa_id": wa_id
            }

            # Actualizar último mensaje del chat
            bot.CHATS[bot.CHATS.index(bot.CURRENT_CHAT)]["last_msg"] = wa_id

            bot.CURRENT_CHAT["last_msg"] = wa_id
            release_clipboard()

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
                parent = get_parent(n)
                done = None
                while not done:
                    parent_data_id = parent.get_attribute("data-id")
                    if parent_data_id:
                        if 'cell-frame-container' not in parent_data_id:
                            parent = get_parent(parent)
                        else:
                            done = True

                # Si es chat de grupo o chat propio, continuar con la siguiente notificación
                is_own_chat = False
                is_group = False
                is_writing = False

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
                            for selector in selectors["writing"]:
                                try:
                                    writing = parent.find_element_by_xpath(selectors["writing"])
                                    is_writing = True
                                except:pass
                            if not is_writing:
                                raise Exception('No está escribiendo')
                        except:
                            try:
                                parent.find_element_by_xpath(selectors["group_event"])
                                is_group = True
                            except:pass

                if is_group or is_own_chat or is_writing:
                    continue
                
                # Ingresar al chat
                bot.CURRENT_CHAT = {}
                parent.click()

                time.sleep(2)
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
        try:
            driver.find_element_by_xpath(selectors["message"])
        except:
            driver.find_element_by_xpath(selectors["message1"])

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
                messages = get_inbounds(driver, selectors)
            else:
                print('Chat propio detectado')
        else:
            print('Chat propio detectado')

        # Formatear y subir mensajes
        if messages != []:
            try:
                messages = make_inbound_messages(driver, selectors, messages)
                
                apis.send_inbounds(messages)
            except Exception as e:
                if bot.SHOW_ERRORS:
                    print("Error al obtener mensajes nuevos")
                    print(e)
        else:
            if bot.SHOW_EX_PRINTS:
                print("No hay mensajes nuevos en este chat")
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print(e)
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

            # Reacción
            reaction = reference_elem.get_attribute("data-testid")
            is_reaction_bubble = ("reaction-bubble" in reaction) if reaction else False
            print(f"Es una reacción: {'SI' if is_reaction_bubble else 'NO'}")

            is_chat_separator = False
            for selector in selectors["chat_separator_class"]:
                if selector in reference_elem.get_attribute("class"):
                    is_chat_separator = True
                    break
            print(f"Es un separador de chat: {'SI' if is_chat_separator else 'NO'}")
            if is_chat_separator:
                try:
                    reference_elem = reference_elem.find_elements_by_xpath(selectors["missed_call_container"])[-1]
                    print("Is missed_call")
                    print("Buscando elemento de mensaje padre")
                    while not reference_elem.get_attribute("data-id"):
                        reference_elem = get_parent(reference_elem)
                except:pass
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element
            if selectors["message_out_class"] in driver.switch_to.active_element.get_attribute("class"):
                message_out_container = None
                for selector in selectors["message_out_container"]:
                    try:
                        message_out_container = driver.find_elements_by_css_selector(selector)[-1]
                        break
                    except:pass
                if message_out_container:
                    reference_elem = message_out_container
                    reference_elem.send_keys(Keys.ARROW_DOWN)
                    reference_elem = driver.switch_to.active_element
            if is_reaction_bubble: # Reacción
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element

                reaction = reference_elem.get_attribute("data-testid")
                is_reaction_bubble = ("reaction-bubble" in reaction) if reaction else False
                print(f"Es una reacción: {'SI' if is_reaction_bubble else 'NO'}")
                if is_reaction_bubble: # Si el último elemento del chat es una reacción
                    reference_elem.send_keys(Keys.ARROW_UP)
                    reference_elem = driver.switch_to.active_element

            if bot.SHOW_EX_PRINTS:
                print("Mensaje en caché ", bot.CURRENT_CHAT["last_msg"])
        except Exception as e:
            print(e)
            try:
                for selector in selectors["unread"]:
                    try:
                        reference_elem = driver.find_element_by_xpath(selectors["unread"])
                        break
                    except:pass
                reference_elem.click()
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element
                if bot.SHOW_EX_PRINTS:
                    print("Hay mensajes no leidos")
            except:
                try:
                    message_out_container = None
                    for selector in selectors["message_out_container"]:
                        try:
                            message_out_container = driver.find_elements_by_css_selector(selector)[-1]
                            break
                        except:pass
                    print(f"Es un mensaje saliente: {'SI' if message_out_container else 'NO'}")
                    if message_out_container:
                        reference_elem = message_out_container
                        reference_elem.send_keys(Keys.ARROW_DOWN)
                        reference_elem = driver.switch_to.active_element
                    else:
                        int("s")
                    if bot.SHOW_EX_PRINTS:
                        print("Navegando a primer mensaje desde ultimo mensaje saliente")
                except:
                    try:
                        message_in_container = None
                        for selector in selectors["message_in_container"]:
                            try:
                                message_in_container = driver.find_elements_by_css_selector(selector)[0]
                                break
                            except:pass
                        first_msg = message_in_container

                        if not first_msg:
                            int("s")
                        if bot.SHOW_EX_PRINTS:
                            print("Obteniendo primer mensaje entrante del chat")
                    except:
                        try:
                            first_msg = driver.find_elements_by_xpath(selectors["missed_call_container"])[-1]
                            if bot.SHOW_EX_PRINTS:
                                print("Obteniendo llamada perdida")

                            print("Buscando elemento de mensaje padre")
                            while not first_msg.get_attribute("data-id"):
                                first_msg = get_parent(first_msg)
                        except:
                            done = True
        
        if not first_msg and not done:
            first_msg = reference_elem

            # Comprobar si es el mensaje de "este chat está cifrado"
            try:
                first_msg.find_element_by_xpath(selectors["encrypted_chat"])[-1] 
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
            except:pass
            # Comprobar si es el mensaje de "mensajes temporales"
            try:
                first_msg.find_element_by_xpath(selectors["temporal_chat"])[-1] 
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
            except:pass

            # Buscar primer mensaje
            while not first_msg.get_attribute("data-id"):
                #print(first_msg.get_attribute("class"), first_msg.get_attribute("data-tab"))

                if bot.SHOW_EX_PRINTS:
                    print("Obteniendo primer mensaje")

                # Comprobar si es un elemento del chat

                # Condiciones
                is_chat_item = False
                for selector in selectors["chat_item_class"]:
                    if selector in first_msg.get_attribute("class"):
                        is_chat_item = True
                        break
                is_unread_sign = False 
                for selector in selectors["unread_class"]:
                    if selector in first_msg.get_attribute("class"):
                        is_unread_sign = True
                        break
                is_shared_contact_action = selectors["shared_contact_action_class"] in first_msg.get_attribute("class")
                reaction = first_msg.get_attribute("data-testid")
                is_reaction_bubble = ("reaction-bubble" in reaction) if reaction else False
                print(f"Es una reacción: {'SI' if is_reaction_bubble else 'NO'}")
                print(f"Es una acción de contacto: {'SI' if (is_shared_contact_action) else 'NO'} ")
                time.sleep(1)

                if is_chat_item or is_unread_sign:
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                elif is_shared_contact_action:
                    print("Navegando desde acción de contacto compartido")
                    print(first_msg.text)
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                    time.sleep(1)
                    print(first_msg.text)
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                    time.sleep(1)
                    is_shared_contact_action = selectors["shared_contact_action_class"] in first_msg.get_attribute("class")
                    if is_shared_contact_action:
                        print(first_msg.text)
                        first_msg.send_keys(Keys.ARROW_UP)
                        first_msg = driver.switch_to.active_element
                        time.sleep(1)
                        print(first_msg.text)
                        first_msg.send_keys(Keys.ARROW_UP)
                        first_msg = driver.switch_to.active_element
                        time.sleep(1)
                elif is_reaction_bubble: # Reacción
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element

                    reaction = first_msg.get_attribute("data-testid")
                    is_reaction_bubble = ("reaction-bubble" in reaction) if reaction else False
                    print(f"Es una reacción: {'SI' if is_reaction_bubble else 'NO'}")
                    if is_reaction_bubble: # Si el último elemento del chat es una reacción
                        first_msg.send_keys(Keys.ARROW_UP)
                        first_msg = driver.switch_to.active_element
                else: # Si no es elemento del chat TAB hasta entrar a la ventana del chat
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
            time.sleep(1)      

        print("Mensaje obtenido")
        print(f"Primer mensaje: {first_msg.get_attribute('data-id')}")

        # Condiciones
        different_data_id = (first_msg.get_attribute("data-id") != bot.CURRENT_CHAT["last_msg"])
        not_msg_out = not(selectors["message_out_class"] in first_msg.get_attribute('class'))

        print(f"Es un mensaje nuevo: {'SI' if (different_data_id and not_msg_out) else 'NO'}")

        # Guardando primer mensaje
        if different_data_id and not_msg_out:
            messages.append(first_msg.get_attribute("data-id"))
            last_msg = first_msg
        else:
            done = True

        # Obtener todos los mensajes nuevos
        print("Revisando mensajes siguientes...")
        while not done:
            try:
                last_msg.send_keys(Keys.ARROW_DOWN)
                next_msg = driver.switch_to.active_element
                if last_msg != next_msg:
                    # Condiciones
                    not_msg_out = not(selectors["message_out_class"] in next_msg.get_attribute('class'))
                    has_data_id = next_msg.get_attribute("data-id")
                    reaction = first_msg.get_attribute("data-testid")
                    not_reaction_bubble = not(("reaction-bubble" in reaction) if reaction else False)
                    print(f"Es una reaction: {'NO' if (not_reaction_bubble) else 'SI'} ")

                    is_message_in = not_msg_out and has_data_id and not_reaction_bubble
                    print(f"Es mensaje entrante: {is_message_in}")

                    if is_message_in:
                        print(f"Añadiendo {next_msg.get_attribute('data-id')}")
                        messages.append(next_msg.get_attribute("data-id"))
                    
                    last_msg = next_msg
                else:
                    done = True
            except:
                done = True

        if messages == [None]:
            messages = []

        print("No hay más mensajes nuevos")

    except:
        if bot.SHOW_EX_PRINTS:
            print("No hay mensajes no leidos")
    
    return messages

def make_inbound_messages(driver, selectors, messages):
    print("Formateando mensajes")
    time.sleep(1)
    result = []
    print(f"Lista de mensajes: {messages}")
    for m in messages:
        wa_id = m
        nombre = ""
        done = None

        # Instanciar mensaje
        count = 0
        while not done:
            try:
                m = driver.find_element_by_xpath('//div[@data-id="' + wa_id + '"]')
                done = True
            except:
                try:
                    driver.find_element_by_xpath(selectors["message"]).click()
                except:
                    driver.find_element_by_xpath(selectors["message1"]).click()
                count += 1
                if count < 10:
                    time.sleep(0.8)
                else:
                    continue

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
                    try:
                        m.find_element_by_xpath(selectors["audio_status"])
                    except:
                        m.find_element_by_xpath(selectors["audio_icon_ptt"])

                no_spam = False
                try:
                    driver.find_element_by_xpath(selectors["no_spam_button"]).click()
                    no_spam = True
                except:pass

                if no_spam:
                    print("Marcado como no-spam")
                    driver.send_keys(Keys.ESCAPE)
                    open_chat(driver, selectors, celular=celular, tipo='ENTRANTE')
                    time.sleep(2)
                    clear_elem(driver, selectors, "search")
                    
                    # Instanciar mensaje
                    done = None
                    while not done:
                        try:
                            m = driver.find_element_by_xpath('//div[@data-id="' + wa_id + '"]')
                            done = True
                        except:
                            try:
                                driver.find_element_by_xpath(selectors["message"]).click()
                            except:
                                driver.find_element_by_xpath(selectors["message1"]).click()
                            time.sleep(0.8)
                    print(f"Mensaje re-instanciado: {m}")
                                
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
                    try:
                        m.find_element_by_xpath(selectors["image_download"]).click()
                        time.sleep(2)
                    except:pass
                    is_attach_inbound = False
                    for selector in selectors["attach_inbound_class"]:
                        if selector in m.get_attribute('class'):
                            is_attach_inbound = True
                            break
                    
                    if not(is_attach_inbound):
                        wait_time = datetime.now() + timedelta(seconds=10)
                        done = None
                        while not done:
                            if datetime.now() < wait_time:
                                is_attach_inbound = False
                                for selector in selectors["attach_inbound_class"]:
                                    if selector in m.get_attribute('class'):
                                        is_attach_inbound = True
                                        break
                                if is_attach_inbound:
                                    done = True
                                else:
                                    time.sleep(1)
                            else:
                                # Revisar si es que el archivo ya no está disponible
                                try:
                                    m.find_element_by_xpath(selectors["image_download"]).click()
                                except:
                                    m.find_element_by_xpath(selectors["thumbnail"]).click()
                                time.sleep(2)
                                
                                try:
                                    for selector in selectors["modal_backdrop"]:
                                        try:
                                            driver.find_element_by_xpath(selector).click()
                                        except:pass
                                    for selector in selectors["modal_body"]:
                                        try:
                                            driver.find_element_by_xpath(selector).click()
                                        except:pass
                                    driver.find_element_by_xpath(selectors["modal_ok_button"]).click()
                                    continue # Continuar con el siguiente elemento
                                except:
                                    driver.find_element_by_xpath(selectors["close_media"]).click()
                                    wait_time = datetime.now() + timedelta(seconds=10)
                    is_image = True
                except:
                    try:
                        try:
                            # Revisando si es un video a partir de un enlace
                            html = m.find_element_by_xpath(selectors["message_text"]).get_attribute("innerHTML")
                            if '<a' in html:
                                is_link = True
                        except:
                            pass
                        
                        if not is_link:
                            m.find_element_by_xpath(selectors["video_button"]).click()
                            is_video = True
                    except:
                        pass
            
            is_attach_inbound = False
            for selector in selectors["attach_inbound_class"]:
                if selector in m.get_attribute('class'):
                    is_attach_inbound = True
                    break

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
                            m.find_element_by_xpath(selectors["download_options"]).click()
                        except:pass
                        try:
                            m.find_element_by_xpath(selectors["message_checkbox"])
                            m.find_element_by_xpath(selectors["close_message_selection"]).click()
                            m.send_keys(Keys.ARROW_RIGHT)
                        except:pass

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

            elif is_attach_inbound:
                try:
                    m.find_element_by_xpath(selectors["attach_inbound_download"]).click()
                except:
                    is_link = True

            if (is_video or is_audio or is_image or is_attach_inbound) and not(is_link):
                if bot.SHOW_EX_PRINTS:
                    print("Descargando...")
                archivo = get_inbound_file()


            # Obtener texto
            try:
                text = None
                for selector in selectors["message_text"]:
                    try:
                        text = m.find_element_by_xpath(selector)
                        break
                    except:pass
                if not text:
                    raise Exception("No se pudo obtener texto")

                html = text.get_attribute("innerHTML")
                # Obtener emojis
                text = re.sub('<img.*?data-plain-text="','',html, flags=re.DOTALL)
                text = re.sub('" style.*?;"','',text, flags=re.DOTALL).replace('>', '')
                # Formatear negrita
                for selector in selectors["message_text_class"]:
                    text = text.replace('<strong class="' + selector + '" data-app-text-template="*${appText}*"', '*')
                text.replace('</strong', '*')
                # Formatear cursiva
                for selector in selectors["message_text_class"]:
                    text = text.replace('<em class="' + selector + '" data-app-text-template="_${appText}_"', '_')
                text.replace('</em', '_')
                # Eliminar link
                text = re.sub('<a.*?copyable-text','',text, flags=re.DOTALL).replace('</a', '')
            except:
                emojis = None
                for selector in selectors["emogi_container"]:
                    try:
                        emojis = m.find_elements_by_xpath(selector)
                        break
                    except:pass

                text = ''
                if emojis:
                    print(f"Hay emojis {emojis}")
                    try:
                        for ec in emojis:
                            print(ec)
                            text += ec.find_element_by_xpath(".//img").get_attribute("data-plain-text")
                    except Exception as e:
                        print(e)
            
            # Obtener contacto compartido
            try:
                m.find_element_by_xpath(selectors["shared_contact_button"]).click()
                time.sleep(2)
                shared_contact_name = ''
                shared_contact_phone = ''
                driver.find_element_by_xpath(selectors["modal_backdrop"]).click()
                for selector in selectors["shared_contact_name"]:
                    try:
                        shared_contact_name = driver.find_element_by_xpath(selector).text
                        break
                    except:pass

                for selector in selectors["shared_contact_phone"]:
                    try:
                        shared_contact_phone = driver.find_element_by_xpath(selector).text
                        break
                    except:pass

                for selector in selectors["chat_info_close"]:
                    try:
                        m.find_element_by_xpath(selector).click()
                        break
                    except:pass
                
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

            # Obtener mención
            try:
                # Obtener grupo
                group_elem = m.find_element_by_xpath(selectors["quoted_message"])
                quoted_text_elements = group_elem.find_elements_by_tag_name("span")
                quoted_group = ""
                quoted_text = ""
                for t in quoted_text_elements:
                    if not 'color' in t.get_attribute("class") and not selectors["quoted_message_text_class"] in t.get_attribute("class"):
                        in_response_group = t.text.replace("Tú", "").replace(" · ", "")
                    if selectors["quoted_message_text_class"] in t.get_attribute("class"):
                        in_response_text = t.text

                in_response = {
                    "grupo": quoted_group,
                    "mensaje": quoted_text 
                }
            except:pass
        else:
            call_text = "Llamada perdida"
            for selector in selectors["missed_call_text"]:
                try:
                    call_text = m.find_element_by_xpath(selectors["missed_call_text"]).text
                except:pass
            text = f"*{call_text}*"

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

    print(result)

    return result

def clear_cache():
    try:
        shutil.rmtree(f'inbound_file_cache{bot.OS_SLASH}{str(bot.BOT_PK)}{bot.OS_SLASH}')
        if bot.SHOW_EX_PRINTS:
            print("Caché limpiado")
    except Exception as e:
        print(e)
        if bot.SHOW_EX_PRINTS:
            print("El caché entrante no se puede limpiar/ya está limpio")

    try:
        shutil.rmtree(f'file_cache{bot.OS_SLASH}{str(bot.BOT_PK)}{bot.OS_SLASH}')
        if bot.SHOW_EX_PRINTS:
            print("Caché limpiado")
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("El caché saliente no se puede limpiar/ya está limpio")