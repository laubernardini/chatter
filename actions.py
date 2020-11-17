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
def get_cel_by_data_id(data):
    return (data.split("false_", 1)[1]).split("@", 1)[0]

def clear_elem(driver, selectors, id):
    driver.find_element_by_xpath(selectors["search"]).clear()
    driver.find_element_by_xpath(selectors["search"]).send_keys(Keys.ESCAPE)

def search(driver, selectors, text):
    # Obtener input de búsqueda
    elem = driver.find_element_by_xpath(selectors["search"])

    # Buscar
    elem.send_keys(text)
    time.sleep(2)

    # Seleccionar la primera opción
    elem.send_keys(Keys.ARROW_DOWN)

    if driver.switch_to.active_element == elem: # Revisa si hubo resultados, sino devuelve None
        return None
    else:
        return elem

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

def send_message(mensaje="", archivo="", celular="", masive=False, driver=None, selectors=None):
    try:
        # Obtener chat
        elem = search(driver, selectors, celular)
        if elem:
            # Abrir chat (si es un chat vacío)
            elem.send_keys(Keys.ENTER)

            # Obtener input de mensaje
            done = None
            while not done:
                try:
                    message = driver.find_element_by_xpath(selectors["message"])
                    done = True
                except:
                    time.sleep(1)

            # Obtener último y guardarlo en caché
            if not(celular in bot.LAST_MSG_CACHE):
                try:
                    bot.LAST_MSG_CACHE = driver.find_elements_by_css_selector(selectors["message_in_container"])[-1].get_attribute("data-id")
                except:
                    pass
            else:
                # Revisar mensajes nuevos en el chat
                check_current_chat(driver=driver, selectors=selectors, archive_chat=False)

            # Preparar mensaje, reemplazar saltos de linea por caracter no utilizado -> `
            mensaje = mensaje.replace("-#", '').replace("#-", '').replace("-*", "*").replace("*-", "*").replace("\r\n", "`").replace("\n\r", "`").replace("\n", "`").replace("\r", "`")

            attach_type = None
            if archivo != "":
                # Resolver tipo de archivo
                attach_type = 'doc'
                for ext in bot.MULTIMEDIA_EXT:
                    if ext in archivo:
                        attach_type = 'multimedia'
                
                # Descargar archivo temporalmente y obtener path
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
                            driver.find_element_by_xpath(selectors["search"]).click()
                            driver.find_element_by_xpath(selectors["preview"]).click()
                            message = driver.find_element_by_xpath(selectors["message_attached"])
                            e = True
                        except:
                            time.sleep(2)
                else:
                    # Enviar archivo
                    e = None
                    while not e:
                        try:
                            driver.find_element_by_xpath(selectors["file_submit"]).click()
                            e = True
                        except:
                            time.sleep(1)

            # Escribir mensaje
            if masive:
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
                for m in mensaje:
                    message.send_keys(m)
                    message.send_keys(Keys.LEFT_SHIFT, Keys.ENTER)
                message.send_keys(Keys.BACKSPACE)

            try:
                if driver.find_elements_by_css_selector(selectors["message_in_container"])[-1].get_attribute("data-id") != bot.LAST_MSG_CACHE:
                    # Revisar en el chat
                    check_current_chat(driver, selectors)
            except:
                pass
            
            # Enviar mensaje
            message.send_keys(Keys.ENTER)

            time.sleep(2)

            # Archivar el chat
            archive(driver, selectors, celular)
            if archivo != "":
                return file_path
        else:
            if bot.SHOW_EX_PRINTS:
                print("Contacto no encontrado")
            clear_elem(driver, selectors, "search")
            return "ERROR"
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error enviando mensaje")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        bot.STATE = "ERROR"
        return "ERROR"

def notification_clicker(driver, selectors):
    try:
        n = driver.find_elements_by_xpath(selectors["notification"])[0]
        time.sleep(2)
        n.click()
        return None
    except:
        if bot.SHOW_EX_PRINTS:
            print("No hay notificaciones")
        return True

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

def check_current_chat(driver, selectors, archive_chat=True):
    # Revisar en el chat
    try:
        driver.find_element_by_xpath(selectors["message"])
        messages = get_inbounds(driver, selectors)
        if messages != []:
            messages = make_inbound_messages(driver, selectors, messages)
            if archive_chat:
                archive(driver, selectors, messages[0]["celular"])
            asyncio.run(apis.send_inbounds(messages))
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("No hay mensajes nuevos en este chat")

def get_inbounds(driver, selectors):
    try:
        done = None
        first_msg = None
        messages = []
        try:
            driver.find_element_by_xpath('//div[@data-id="' + bot.LAST_MSG_CACHE + '"]').send_keys(Keys.ARROW_DOWN)
            if selectors["chat_separator_class"] in driver.switch_to.active_element.get_attribute("class"):
                driver.find_elements_by_xpath(selectors["missed_call_container"])[-1].send_keys(Keys.ARROW_DOWN)
            if selectors["message_out_class"] in driver.switch_to.active_element.get_attribute("class"):
                driver.find_elements_by_css_selector(selectors["message_out_container"])[-1].send_keys(Keys.ARROW_DOWN)
            if bot.SHOW_EX_PRINTS:
                print("Mensaje en caché ", bot.LAST_MSG_CACHE)
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
            while not first_msg.get_attribute("data-id"):
                if first_msg.get_attribute("class") == selectors["input_class"]:
                    first_msg.send_keys(Keys.TAB)
                    first_msg = driver.switch_to.active_element
                if bot.SHOW_EX_PRINTS:
                    print("Obteniendo primer mensaje")
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
        
        if first_msg.get_attribute("data-id") != bot.LAST_MSG_CACHE and (selectors["message_in_class"] in first_msg.get_attribute('class')):
            messages.append(first_msg)
            last_msg = first_msg
            bot.LAST_MSG_CACHE = last_msg.get_attribute("data-id")
        else:
            try:
                # Si es una llamada perdida, generar respuesta automática
                first_msg.find_element_by_xpath(selectors["missed_call"])
                if bot.SHOW_EX_PRINTS:
                    print("Llamada perdida, generando respuesta")
                if first_msg.get_attribute("data-id") != bot.LAST_MSG_CACHE:
                    bot.LAST_MSG_CACHE = first_msg.get_attribute("data-id")
                    bot.AUTO_RESPONSES.append({
                        "celular": get_cel_by_data_id(first_msg.get_attribute("data-id")),
                        "mensaje": bot.CALL_RESPONSE, 
                        "archivo": ""
                    })
                    last_msg = first_msg
                else:
                    done = True
            except:
                done = True

        while not done:
            try:
                last_msg.send_keys(Keys.ARROW_DOWN)
                next_msg = driver.switch_to.active_element
                if last_msg != next_msg:
                    if (selectors["message_in_class"] in next_msg.get_attribute('class')):
                        messages.append(next_msg)
                        bot.LAST_MSG_CACHE = next_msg.get_attribute("data-id")
                    else:
                        try:
                            next_msg.find_element_by_xpath(selectors["missed_call"])
                            # Si es una llamada perdida, generar respuesta automática
                            if bot.SHOW_EX_PRINTS:
                                print("Llamada perdida, generando respuesta")
                            bot.LAST_MSG_CACHE = next_msg.get_attribute("data-id")
                            bot.AUTO_RESPONSES.append({
                                "celular": get_cel_by_data_id(next_msg.get_attribute("data-id")),
                                "mensaje": bot.CALL_RESPONSE, 
                                "archivo": ""
                            })
                        except:
                            pass
                    last_msg = next_msg
                else:
                    done = True
            except:
                done = True

        return messages
        
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("No hay mensajes no leidos")
        if bot.SHOW_ERRORS:
            print(e)
        return []

def make_inbound_messages(driver, selectors, messages):
    result = []
    celular = get_cel_by_data_id(messages[0].get_attribute("data-id"))
    for m in messages:
        archivo = ""
        is_audio = False
        is_image = False
        is_video = False
        is_call = False
        try:
            try:
                m.find_element_by_xpath(selectors["audio_icon"])
            except:
                m.find_element_by_xpath(selectors["audio_status"])
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
            m.find_element_by_xpath(selectors["attach_inbound_download"]).click()
 
        if is_video or is_audio or is_image or (selectors["attach_inbound_class"] in m.get_attribute("class")):
            if bot.SHOW_EX_PRINTS:
                print("Descargando...")
            archivo = get_inbound_file()

        try:
            text = m.find_element_by_xpath(selectors["message_text"])
            html = text.get_attribute("innerHTML")
            text = re.sub('<img.*?data-plain-text="','',html, flags=re.DOTALL).replace('">', '')
        except:
            try:
                emogis = m.find_elements_by_xpath(selectors["emogi_container"])
                text = ''
                for ec in emogis:
                    text += ec.find_element_by_xpath(".//img").get_attribute("data-plain-text")
            except Exception as e:
                if bot.SHOW_ERRORS:
                    print(e)
        text = " " if text == '' else text

        # Omitir mensaje vacío
        if archivo == '' and text == ' ':
            continue

        result.append({
            "data-id": m.get_attribute("data-id"),
            "celular": celular,
            "mensaje": text,
            "archivo": archivo
        })

    return result

def clear_cache():
    try:
        shutil.rmtree('inbound_file_cache')
        shutil.rmtree('file_cache')
        if bot.SHOW_EX_PRINTS:
            print("Caché limpiado")
    except Exception as e:
        if bot.SHOW_EX_PRINTS:
            print("El caché no se puede limpiar/ya está limpio")

