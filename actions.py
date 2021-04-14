import os
import shutil
import re

import bot
import apis
import time
import asyncio
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

    # Obtener celular
    for i in info:
        if "+" in i.text:
            celular = i.text
            break
    
    # Obtener nombre
    try:
        nombre = driver.find_element_by_xpath(selectors["contact_name"]).text
    except:
        try:
            nombre = driver.find_element_by_xpath(selectors["contact_name1"]).text
        except:
            try:
                nombre = driver.find_element_by_xpath(selectors["agended_contact_name"]).text
            except:
                nombre = driver.find_element_by_xpath(selectors["agended_contact_name1"]).text

    result = {
        "nombre": nombre,
        "celular": cel_formatter(celular),
    }

    # Cerrar info del contacto
    driver.find_element_by_xpath(selectors["chat_info_close"]).click()

    return result

# Búsqueda
def clear_elem(driver, selectors, id):
    driver.find_element_by_xpath(selectors[id]).clear()
    driver.find_element_by_xpath(selectors[id]).send_keys(Keys.ESCAPE)

def search(driver, selectors, text):
    # Obtener input de búsqueda
    result = None
    no_result = False    
    elem = driver.find_element_by_xpath(selectors["search"])
    
    # Buscar
    elem.send_keys(text)
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
            if driver.switch_to.active_element != elem:
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
    while not loaded:
        try:
            archivo = max(['inbound_file_cache' + bot.OS_SLASH + f for f in os.listdir('inbound_file_cache')],key=os.path.getctime)
            if archivo != bot.LAST_FILE:
                loaded = True
                bot.LAST_FILE = archivo
                if bot.SHOW_EX_PRINTS:
                    print("Archivo obtenido")
        except:
            time.sleep(2)
    return archivo

def send_message(mensaje="", archivo="", celular="", masive=False, last_msg=None, driver=None, selectors=None):
    try:
        # Obtener chat
        elem = search(driver, selectors, celular)
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
            mensaje = mensaje.replace("-#", '').replace("#-", '').replace("-*", "*").replace("*-", "*").replace("-_", "_").replace("_-", "_").replace("\r\n", "`").replace("\n\r", "`").replace("\n", "`").replace("\r", "`")
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
                    f = open('file_cache' + bot.OS_SLASH + archivo)
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

                driver.find_element_by_xpath(selectors["preview"]).click()
                
                if attach_type == 'multimedia':
                    # Obtener input de mensaje
                    e = None
                    while not e:
                        try:
                            message = driver.find_element_by_xpath(selectors["message_attached"])
                            e = True
                        except:
                            time.sleep(1)
                            driver.find_element_by_xpath(selectors["search"]).click()
                            driver.find_element_by_xpath(selectors["preview"]).click()
                else:
                    # Enviar archivo
                    e = None
                    while not e:
                        try:
                            driver.find_element_by_xpath(selectors["file_submit"]).click()
                            e = True
                        except:
                            time.sleep(1)
            #print("Archivo listo")

            # Escribir mensaje
            if False:#masive:
                # "Teclear" mensaje
                for letra in mensaje:
                    if letra != '`':
                        message.send_keys(letra)
                    else:
                        message.send_keys(Keys.LEFT_SHIFT, Keys.ENTER)
                    time.sleep(0.02)
            else:
                # Pegar mensaje
                mensaje = mensaje.split("`")
                print('\n', mensaje, '\n')
                for m in mensaje:
                    message.send_keys(m)
                    message.send_keys(Keys.LEFT_SHIFT, Keys.ENTER)
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
            print("Error enviando mensaje")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        result = {
            "estado": "ERROR", 
            "wa_id": None
        }
        return result

def update_current_chat(driver, selectors, last_msg=None, celular=None):
    if not celular:
        chat_info = get_data_by_chat_info(driver, selectors)
    else:
        chat_info = {
            "nombre": celular,
            "celular": celular
        }
    chat = get_chat_by_chat_name(chat_info["celular"])
    if not chat:
        # Pedir último mensaje
        if not last_msg:
            last_msg = apis.get_last_msg(celular=chat_info["celular"])

        chat = create_chat_by_data(nombre=chat_info["nombre"], celular=chat_info["celular"], last_msg=last_msg)
    
    # Indicar chat en ejecución
    bot.CURRENT_CHAT = get_chat_by_chat_name(chat["celular"])

def notification_clicker(driver, selectors):
    done = None
    try:
        notifications = driver.find_elements_by_xpath(selectors["notification"])
        for n in notifications:
            if n.get_attribute("aria-label") == None:
                parent = n.find_element_by_xpath('.//..//..//..//..')
                
                # Si es chat de grupo, continuar con la siguiente notificación
                is_group = False
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

                if is_group:
                    continue
                
                # Ingresar al chat
                bot.CURRENT_CHAT = {}
                n.click()

                time.sleep(2)
                done = True
                if done:
                    break

    except Exception as e:
        print(e)
        if bot.SHOW_EX_PRINTS:
            print("No hay notificaciones")
            
    return done

# Función en desuso
def readed_chat_clicker(driver, selectors):
    try:
        r = driver.find_elements_by_xpath(selectors["readed_chat"])[0]
        time.sleep(2)
        r.click()
        return None
    except:
        if bot.SHOW_EX_PRINTS:
            print("No hay notificaciones")
        return True

def check_current_chat(driver, selectors, chat=None): # Obtener y subir mensajes nuevos
    try:
        # Comprobar chat abierto
        driver.find_element_by_xpath(selectors["message"])
        if bot.SHOW_EX_PRINTS:
            print("Buscando mensajes nuevos")
        
        # Definir sobre qué chat se trabaja
        if not chat:
            update_current_chat(driver, selectors)
        
        # Obtener id's de mensajes nuevos
        messages = []
        try:
            messages = get_inbounds(driver, selectors)
        except Exception as e:
            if bot.SHOW_ERRORS:
                print("Error al obtener mensajes nuevos")
                print(e)

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

        # Localizar elemento de mensaje
        try:
            driver.find_element_by_xpath('//div[@data-id="' + bot.CURRENT_CHAT["last_msg"] + '"]').send_keys(Keys.ARROW_DOWN)
            if selectors["chat_separator_class"] in driver.switch_to.active_element.get_attribute("class"):
                driver.find_elements_by_xpath(selectors["missed_call_container"])[-1].send_keys(Keys.ARROW_DOWN)
            if selectors["message_out_class"] in driver.switch_to.active_element.get_attribute("class"):
                driver.find_elements_by_css_selector(selectors["message_out_container"])[-1].send_keys(Keys.ARROW_DOWN)
            if bot.SHOW_EX_PRINTS:
                print("Mensaje en caché ", bot.CURRENT_CHAT["last_msg"])
        except:
            try:
                driver.find_element_by_xpath(selectors["unread"]).click()
                driver.find_element_by_xpath(selectors["unread"]).send_keys(Keys.ARROW_DOWN)
                if bot.SHOW_EX_PRINTS:
                    print("Hay mensajes no leidos")
            except:
                try:
                    driver.find_elements_by_css_selector(selectors["message_out_container"])[-1].send_keys(Keys.ARROW_DOWN)
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
            if driver.switch_to.active_element.get_attribute("class") == selectors["input_class"]:
                driver.switch_to.active_element.send_keys(Keys.TAB)
            first_msg = driver.switch_to.active_element
            try:
                first_msg.find_element_by_xpath(selectors["encrypted_chat"]) # Comprobar si es el mensaje de "este chat está cifrado"
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
            except:
                pass

            while not first_msg.get_attribute("data-id"):
                if first_msg.get_attribute("class") == selectors["input_class"]:
                    first_msg.send_keys(Keys.TAB)
                    first_msg = driver.switch_to.active_element
                if bot.SHOW_EX_PRINTS:
                    print("Obteniendo primer mensaje")
                
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
                try:
                    first_msg.find_element_by_xpath(selectors["encrypted_chat"]) # Comprobar si es el mensaje de "este chat está cifrado"
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                except:
                    pass
        
        # Condiciones
        different_data_id = (first_msg.get_attribute("data-id") != bot.CURRENT_CHAT["last_msg"])
        not_msg_out = not(selectors["message_out_class"] in first_msg.get_attribute('class'))

        # Guardando primer mensaje
        if different_data_id and not_msg_out:
            messages.append(first_msg.get_attribute("data-id"))
            last_msg = first_msg
        else:
            done = True

        while not done:
            try:
                last_msg.send_keys(Keys.ARROW_DOWN)
                next_msg = driver.switch_to.active_element
                if last_msg != next_msg:
                    # Condiciones
                    not_msg_out = not(selectors["message_out_class"] in next_msg.get_attribute('class'))

                    if not_msg_out:
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
                driver.find_element_by_xpath(selectors["message_in_container"]).send_keys(Keys.ARROW_UP)

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
                            m.find_element_by_xpath(selectors["audio_download"]).click()
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
                        pass
                
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
                # Obtener emogis
                text = re.sub('<img.*?data-plain-text="','',html, flags=re.DOTALL).replace('">', '')
                # Formatear negrita
                text = text.replace('<strong class="_1VzZY selectable-text invisible-space copyable-text" data-app-text-template="*${appText}*', '-*').replace('</strong>', '*-')
                # Formatear cursiva
                text = text.replace('<em class="_1VzZY selectable-text invisible-space copyable-text" data-app-text-template="_${appText}_', '-_').replace('</em>', '_-')
                # Eliminar link
                text = re.sub('<a.*?copyable-text','',text, flags=re.DOTALL).replace('</a>', '')
                text = re.sub('<a.*?">','',text, flags=re.DOTALL).replace('</a>', '')
            except:
                try:
                    emogis = m.find_elements_by_xpath(selectors["emogi_container"])
                    text = ''
                    for ec in emogis:
                        text += ec.find_element_by_xpath(".//img").get_attribute("data-plain-text")
                except:
                    pass
            
            # Obtener contacto compartido
            try:
                m.find_element_by_xpath(selectors["shared_contact_button"]).click()
                time.sleep(2)
                shared_contact_name = ''
                shared_contact_phone = ''
                try:
                    shared_contact_name = driver.find_element_by_xpath(selectors["shared_contact_name"]).text
                except:
                    try:
                        shared_contact_name = driver.find_element_by_xpath(selectors["shared_contact_name1"]).text
                    except:
                        pass

                try:
                    shared_contact_phone = driver.find_element_by_xpath(selectors["shared_contact_phone"]).text
                except:
                    try:
                        shared_contact_phone = driver.find_element_by_xpath(selectors["shared_contact_phone1"]).text
                    except:
                        pass

                m.find_element_by_xpath(selectors["chat_info_close"]).click()
                time.sleep(2)
                
                if shared_contact_phone != '': 
                    text = "-*Contacto*-\n-_Nombre:_- " + shared_contact_name + "\n-_Celular:_- " + shared_contact_phone
            except:
                pass

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
            text = "-*" + m.find_element_by_xpath(selectors["missed_call_text"]).text + "*-"

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
        shutil.rmtree('inbound_file_cache')
        if bot.SHOW_EX_PRINTS:
            print("Caché limpiado")
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("El caché entrante no se puede limpiar/ya está limpio")

    try:
        shutil.rmtree('file_cache')
        if bot.SHOW_EX_PRINTS:
            print("Caché limpiado")
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("El caché saliente no se puede limpiar/ya está limpio")

