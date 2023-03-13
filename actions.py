import sys, os, time, pyperclip

import bot

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
    if f":{bot.PHONE}:" in pyperclip.paste() or pyperclip.paste() == '':
        pyperclip.copy(':f:')

def get_parent(element):
    return element.find_element_by_xpath('..')

def cel_formatter(celular): # Formatear celular
    chars_to_delete = [' ', '+', '-', '(', ')']
    for c in chars_to_delete:
        celular = celular.replace(c, '')
    
    if celular.startswith('0'):
        celular = celular[1:]
    
    return celular

def get_msg_data_id(msg):
    data_id = None
    if not msg.get_attribute('data-id'):
        msg_parent = get_parent(msg)
        if msg_parent.get_attribute('data-id'):
            data_id = msg_parent.get_attribute('data-id')
    else:
        data_id = msg.get_attribute('data-id')
    return data_id

def close_confirm_popup(driver, selectors):
    # Instanciar modal
    try:
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
        
        modal.find_element_by_xpath("modal_ok_button").click()
    except Exception as e:
        print(e)
        print("No hay popup")

def set_tabindex(elem, driver, selectors):
    if not elem.get_attribute('tabindex'):
        driver.execute_script('arguments[0].setAttribute("tabindex", "-1")', elem)

def set_focusable_item_class(elem, driver, selectors):
    if elem.get_attribute('data-id'):
        if selectors["navigation_item_class"] not in elem.get_attribute('class'):
            driver.execute_script('arguments[0].classList.add("focusable-list-item")', elem)

# Búsqueda
def clear_elem(driver, selectors, id):
    elem = driver.find_element_by_xpath(selectors[id])
    if id == "search":
        clear_search(driver, selectors, elem)
    else:
        elem.clear()
        elem.send_keys(Keys.ESCAPE)

def clear_search(driver, selectors, elem):
    try:
        cancel_icon = get_parent(get_parent(get_parent(elem))).find_element_by_xpath(selectors["clear_search"])
        get_parent(cancel_icon).click()
    except Exception as e:
        print(e)
        print("No se pudo limpiar el buscador")

def search(driver, selectors, text):
    print("Buscando: ", text)
    # Obtener input de búsqueda
    result = None
    has_results = True
    side = driver.find_element_by_xpath(selectors["side"]) 
    elem = side.find_element_by_xpath(selectors["search"])
    
    # Buscar
    elem.send_keys(text)
    #driver.execute_script("arguments[0].innerText = `{}`".format(text), elem)
    #elem.send_keys('.')
    #elem.send_keys(Keys.BACKSPACE)
    time.sleep(2)

    done = None
    while not done:
        try:
            searching = driver.find_element_by_xpath(selectors["searching"])
            try:
                searching.find_element_by_xpath(selectors["no_chat_found"])
                has_results = False
                done = True
            except:
                done = True
        except:
            done = True
    
    if has_results:
        has_results = False
        try:
            section_headers = side.find_elements_by_xpath(selectors["section_header"])
            for section in section_headers:
                if 'chats' in section.text.lower() or 'contact' in section.text.lower():
                    has_results = True
                    break
        except Exception as e:
            print(e)
    
    if has_results:
        # Seleccionar la primera opción
        elem.send_keys(Keys.ARROW_DOWN)
        elem.send_keys(Keys.ENTER)
        if text != bot.PHONE:
            result = True
        else:
            try:
                chat_header = driver.find_element_by_xpath(selectors["chat_header"])
                you_label = False
                try:
                    chat_header.find_element_by_xpath(selectors["chat_header_you_label"])
                    you_label = True
                except:
                    you_label = (cel_formatter(chat_header.find_element_by_xpath(selectors["chat_name_header"]).text) == bot.PHONE)

                result = you_label
            except:pass
    else:
        clear_elem(driver, selectors, "search")
        
    return result

def chat_init(driver, selectors, celular):
    clear_elem(driver, selectors, "search")

    # Verificar chat propio abierto
    done = None
    while not done:
        has_result = search(driver, selectors, bot.PHONE)
        clear_elem(driver, selectors, "search")
        done = has_result
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

def open_chat(driver, selectors, celular, init):
    elem = None
    elem = search(driver, selectors, celular)

    if init and not elem:
        elem = chat_init(driver, selectors, celular)
        
    # Descartar cruce de chat
    if elem:
        try:
            chat_header = driver.find_element_by_xpath(selectors["chat_header"])
            chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header"])
            print('Chat name: ', chat_name_header.text)
            if bot.PHONE == cel_formatter(chat_name_header.text):
                elem = None
        except:
            elem = None

    return elem

def send_message(mensaje="", celular="", driver=None, selectors=None, init=False):
    try:
        elem = open_chat(driver, selectors, celular, init)
        new_message_input = False

        # Enviar mensaje
        if elem:
            clear_elem(driver, selectors, "search")

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

            time.sleep(2)

            # Escribir mensaje
            if new_message_input:
                act = ActionChains(driver)
                act.click(message)

                # Manejo del clipboard
                text = mensaje.replace(':f:', "") + f':{bot.PHONE}:'
                while pyperclip.paste() != text:
                    print(f"Esperando {bot.SLEEP_TIME} segundos")
                    time.sleep(bot.SLEEP_TIME)
                    while not f":{bot.PHONE}:" in pyperclip.paste():
                        wait_and_set(text, bot.CLIPBOARD_SLEEP_TIME)
                
                # Pegar mensaje
                act.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
                time.sleep(0.5)

                # Limpiar código y liberar clipboard
                act.click(message)
                time.sleep(0.5)
                act.key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL)
                act.send_keys(Keys.BACKSPACE)
                for d in bot.PHONE:
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

            # Cerrar chat
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

            release_clipboard()
        else:
            if bot.SHOW_ERRORS:
                print("Chat no encontrado")
            clear_elem(driver, selectors, "search")
        
        return "OK"
    except Exception as e:
        if bot.SHOW_ERRORS:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Error enviando mensaje")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
            print(os.path.split(exc_tb.tb_frame.f_code.co_filename)[1], ", linea ", exc_tb.tb_lineno)
            
        return "ERROR"

def notification_clicker(driver, selectors):
    notification_resolved = False
    try:
        notifications = driver.find_elements_by_xpath(selectors["notification"])
        print(f"Notificaciones: {len(notifications)}")
        for n in notifications:
            parent = get_parent(n)
            done = None
            while not done:
                parent_data_id = parent.get_attribute("data-testid")
                if parent_data_id:
                    if 'cell-frame-container' not in parent_data_id:
                        parent = get_parent(parent)
                    else:
                        done = True
                else:
                    parent = get_parent(parent)

            # Si es chat de grupo o chat propio, continuar con la siguiente notificación
            is_permitter_phone = False
            conversation_name = ""

            try:
                conversation_name = parent.find_element_by_xpath(selectors["conversation_name"])
                conversation_name = conversation_name.find_element_by_xpath(".//span[@dir='auto']").text
                print(f'Conversación: {conversation_name}, BOT PHONE: {bot.PHONE}')
                formatted_conv_name = cel_formatter(conversation_name)
                if formatted_conv_name in bot.PHONES_LIST:
                    is_permitter_phone = True
            except:pass
            
            print("Noti except conditions:", not is_permitter_phone)
            if not is_permitter_phone:
                continue
            
            # Ingresar al chat
            parent = get_parent(n)
            done = None
            while not done:
                print(f"Parent class: {parent.get_attribute('class')}, {parent.get_attribute('data-testid')}, {parent.get_attribute('role')}")
                parent.click()
                time.sleep(1)
                n_count = len(driver.find_elements_by_xpath(selectors["notification"]))
                if n_count < len(notifications):
                    done = True
                else:
                    parent = get_parent(parent)
            print("Notificación abierta")
            notification_resolved = True
            time.sleep(1)
            break
    except Exception as e:
        print(e)
        if bot.SHOW_EX_PRINTS:
            print("No hay notificaciones")
            
    return notification_resolved

def get_inbounds(driver, selectors):
    response = None
    try:
        done = None
        first_msg = None
        reference_elem = None
        has_data_id = None

        is_unread = False
        is_from_outbound = False
        is_first_msg = False

        # Unread message
        if not reference_elem:
            for selector in selectors["unread"]:
                try:
                    reference_elem = driver.find_element_by_xpath(selector)
                    is_unread = True
                    break
                except:pass
            
            if is_unread:
                reference_elem.click()
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element
                if bot.SHOW_EX_PRINTS:
                    print("Hay mensajes no leidos")

        # From last outbound
        if not reference_elem:
            try:
                reference_elem = driver.find_elements_by_css_selector(selectors["message_out_container"])[-1]
                is_from_outbound = True
            except:pass
            print(f"Es un mensaje saliente: {'SI' if is_from_outbound else 'NO'}")

            if is_from_outbound:
                set_tabindex(reference_elem, driver, selectors)
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element

                if bot.SHOW_EX_PRINTS:
                    print("Navegando a primer mensaje desde ultimo mensaje saliente")

        # First message of chat
        if not reference_elem:
            try:
                reference_elem = driver.find_elements_by_css_selector(selectors["message_in_container"])[0]
                is_first_msg = True
            except:pass

            if is_first_msg:
                set_tabindex(reference_elem, driver, selectors)
                first_msg = reference_elem
                if bot.SHOW_EX_PRINTS:
                    print("Obteniendo primer mensaje entrante del chat")

        # Skip
        if not reference_elem:
            done = True
        
        if not first_msg and not done:
            set_tabindex(reference_elem, driver, selectors)
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
            while not get_msg_data_id(first_msg):
                set_tabindex(first_msg, driver, selectors)

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
                time.sleep(1)

                if is_chat_item or is_unread_sign:
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                else: # Si no es elemento del chat TAB hasta entrar a la ventana del chat
                    first_msg.send_keys(Keys.TAB)
                    first_msg = driver.switch_to.active_element
                    time.sleep(0.5)
                
                # Comprobar si es el mensaje de "este chat está cifrado"
                try:
                    first_msg.find_element_by_xpath(selectors["encrypted_chat"])
                    set_tabindex(first_msg, driver, selectors)
                    first_msg.send_keys(Keys.ARROW_DOWN)
                    first_msg = driver.switch_to.active_element
                except:pass
            time.sleep(1)      

        first_msg_data_id = get_msg_data_id(first_msg)
        print("Mensaje obtenido")
        print(f"Primer mensaje: {first_msg_data_id}")

        # Condiciones
        not_msg_out = ('false' in first_msg_data_id) if first_msg_data_id else False

        print(f"Es un mensaje nuevo: {'SI' if (not_msg_out) else 'NO'}")

        
        # Guardando primer mensaje
        if not_msg_out:
            if bot.START_MSG_CODE in first_msg.text and bot.CHATTER_CODE in first_msg.text:
                response = first_msg_data_id
                done = True
            else:
                last_msg = first_msg
        else:
            done = True

        # Obtener todos los mensajes nuevos
        print("Revisando mensajes siguientes...")
        while not done or not response:
            try:
                set_focusable_item_class(last_msg, driver, selectors)
                set_tabindex(last_msg, driver, selectors)
                last_msg.send_keys(Keys.ARROW_DOWN)
                next_msg = driver.switch_to.active_element
                if last_msg != next_msg:
                    # Condiciones
                    has_data_id = get_msg_data_id(next_msg)
                    not_msg_out = False
                    if has_data_id:
                        not_msg_out = 'false' in get_msg_data_id(next_msg)
                    is_message_in = not_msg_out and has_data_id
                    print(f"Es mensaje entrante: {is_message_in}")

                    if is_message_in:
                        if bot.START_MSG_CODE in next_msg.text and bot.CHATTER_CODE in next_msg.text:
                            response = has_data_id
                            done = True
                        else:
                            last_msg = first_msg

                    last_msg = next_msg
                else:
                    done = True
            except:
                done = True

        print("No hay más mensajes nuevos")
    except Exception as e:
        print(e)
        if bot.SHOW_EX_PRINTS:
            print("No hay mensajes no leidos")
    
    return response