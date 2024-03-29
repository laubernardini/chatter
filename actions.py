import sys, os, time, pyperclip

import bot
from tools import * 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import By

# Acciones
def get_input(driver, selectors, key):
    input_element = None
    # Obtener input de mensaje
    done = None
    while not done:
        try:
            input_element = get_element(driver, selectors[key])
            input_element.click()
            done = True
        except:pass
        
        time.sleep(1)
    print("Conversación lista")

    return input_element

def close_confirm_popup(driver, selectors):
    # Instanciar modal
    try:
        modal_elem_list = get_elements(parent=driver, selector=selectors["modal"])
        modal_elem_list = modal_elem_list if modal_elem_list else []
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
        click_element(parent=driver, selector=selectors["modal_body"])
        
        click_element(parent=driver, selector=selectors["modal_ok_button"])
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
def clear_elem(driver, selectors, id, text=""):
    if id == "search":
        clear_search(driver, selectors, text)
    else:
        elem = get_element(parent=driver, selector=selectors[id])
        elem.clear()
        elem.send_keys(Keys.ESCAPE)

def clear_search(driver, selectors, text):
    if not (click_element(parent=driver, selector=selectors["clear_search"])):
        try:
            elem = get_element(parent=driver, selector=selectors["search"])
            ActionChains(driver).click(elem).perform()
            ActionChains(driver).key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL).perform()

            act = ActionChains(driver)
            for d in text:
                act.send_keys(Keys.BACKSPACE)
                
            act.perform()
        except Exception as e:
            print(e)
            print("No se pudo limpiar el buscador")

def search(driver, selectors, text):
    print("Buscando: ", text)
    # Obtener input de búsqueda
    result = None
    has_results = True

    elem = get_element(parent=driver, selector=selectors["search"])

    if not elem:
        return result
    
    # Buscar
    elem.send_keys(text)
    
    time.sleep(2)

    done = None
    while not done:
        if get_element(parent=driver, selector=selectors["searching"]):
            if get_element(parent=driver, selector=selectors["no_chat_found"]):
                has_results = False
                done = True
            else:
                done = True
        else:
            done = True
    
    has_results = get_element(parent=driver, selector=selectors["chats_section"]) or get_element(parent=driver, selector=selectors["contacts_section"])
    
    if has_results:
        # Seleccionar la primera opción
        elem.send_keys(Keys.ARROW_DOWN)
        elem.send_keys(Keys.ENTER)
        if text != bot.PHONE:
            result = True
        else:
            chat_header = get_element(parent=driver, selector=selectors["chat_header"])
            you_label = False
            if chat_header:
                if get_element(parent=chat_header, selector=selectors["chat_header_you_label"]):
                    you_label = True
                else:
                    you_label = cel_formatter(get_element(parent=chat_header, selector=selectors["chat_name_header"]).text) == bot.PHONE

            result = you_label
    else:
        clear_elem(driver, selectors, "search", text)
        
    return result

def chat_init(driver, selectors, celular):
    clear_elem(driver, selectors, "search", celular)

    # Verificar chat propio abierto
    done = None
    while not done:
        search(driver, selectors, bot.PHONE)
        clear_elem(driver, selectors, "search", celular)

        chat_header = get_element(parent=driver, selector=selectors["chat_header"])
        you_label = False
        if chat_header:
            if get_element(parent=chat_header, selector=selectors["chat_header_you_label"]):
                you_label = True
            else:
                you_label = cel_formatter(get_element(parent=chat_header, selector=selectors["chat_name_header"]).text) == bot.PHONE
        done = you_label

        time.sleep(1)

    # Instanciar input mensaje
    done = None
    while not done:
        own_chat_message = get_element(parent=driver, selector=selectors["message"])
        if own_chat_message:
            done = True
        else:
            time.sleep(1)
    
    time.sleep(1)
    link = f"https://wa.me/{celular}"
    for char in link:
        own_chat_message.send_keys(char)
    own_chat_message.send_keys(Keys.ENTER)
    
    # Esperar link
    done = None
    while not done:
        done = click_element(parent=driver, selector=f"//a[@href='https://wa.me/{celular}']")
        if not done:
            time.sleep(2)
    
    # Popup
    done = None
    while not done:
        print("Esperando chat")
        modal_elem_list = get_elements(parent=driver, selector=selectors["modal"])
        modal_elem_list = modal_elem_list if modal_elem_list else []
        if len(modal_elem_list) > 0:
            loadig_confirm = click_element(parent=driver, selector=selectors["modal_iniciando"])
            
            if loadig_confirm:
                time.sleep(0.5)
            else:
                done = True
        else:
            chat_header = get_element(parent=driver, selector=selectors["chat_header"])
            you_label = False
            if chat_header:
                if get_element(parent=chat_header, selector=selectors["chat_header_you_label"]):
                    you_label = True
                else:
                    you_label = cel_formatter(get_element(parent=chat_header, selector=selectors["chat_name_header"]).text) == bot.PHONE

                done = (not you_label)
    
    # Instanciar modal
    modal_elem_list = get_elements(parent=driver, selector=selectors["modal"])
    modal_elem_list = modal_elem_list if modal_elem_list else []
    print(f"Modal elem: {len(modal_elem_list)}")
    modal = None
    for m in modal_elem_list:
        print(f"Modal tabindex: {m.get_attribute('tabindex')}")
        if not m.get_attribute("tabindex") or m.get_attribute("tabindex") != '-1':
            modal = m
            done = True
            break
    
    if modal:
        try:
            # Click en modal
            click_element(parent=modal, selector=selectors["modal_body"])

            # Comprobar número inválido
            modal_text = get_element(parent=modal, selector=selectors["modal_text"])
            if modal_text:
                msg = modal_text.text
                print(msg)
                if "inválido" in msg:
                    click_element(parent=modal, selector=selectors["modal_ok_button"])
                    elem = False
                else:
                    elem = True 
            else:
                elem = True
        except:
            elem = True
    else:
        elem = True

    if elem:
        print("Nuevo chat iniciado")
    else:
        print("Número inválido")
    
    return elem

def open_chat(driver, selectors, celular, init):
    elem = None
    elem = search(driver, selectors, celular)

    if init and not elem:
        elem = chat_init(driver, selectors, celular)
        
    # Descartar cruce de chat
    if elem:
        done = None
        while not done:
            try:
                chat_header = get_element(parent=driver, selector=selectors["chat_header"])
                you_label = False
                if chat_header:
                    if get_element(parent=chat_header, selector=selectors["chat_header_you_label"]):
                        you_label = True
                    else:
                        you_label = cel_formatter(get_element(parent=chat_header, selector=selectors["chat_name_header"]).text) == bot.PHONE
                elem = not you_label
                done = True
            except:
                time.sleep(0.2)

    return elem

def send_message(mensaje="", celular="", driver=None, selectors=None, init=False):
    try:
        elem = open_chat(driver, selectors, celular, init)

        # Enviar mensaje
        if elem:
            # Escribir mensaje
            message_input = get_input(driver, selectors, 'message')
            write_and_send(driver, selectors, message_input, mensaje)
            
            # Cerrar chat
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

            release_clipboard()
        else:
            if bot.SHOW_ERRORS:
                print("Chat no encontrado")
            clear_elem(driver, selectors, "search", celular)
        
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
        notifications = get_elements(parent=driver, selector=selectors["notification"])
        notifications = notifications if notifications else []
        print(f"Notificaciones: {len(notifications)}")
        for n in notifications:
            parent = get_parent(n)
            done = None
            while not done:
                parent_data_id = parent.get_attribute("role")
                if parent_data_id:
                    if 'listitem' not in parent_data_id:
                        parent = get_parent(parent)
                    else:
                        done = True
                else:
                    parent = get_parent(parent)

            # Si es chat de grupo o chat propio, continuar con la siguiente notificación
            is_permitter_phone = False
            is_own_chat = False
            conversation_name = ""

            try:
                conversation_name = get_element(parent=parent, selector=selectors["conversation_name"])
                conversation_name = get_element(parent=conversation_name, selector=".//span[@dir='auto']").text
                print(f'Conversación: {conversation_name}, BOT PHONE: {bot.PHONE}')
                formatted_conv_name = cel_formatter(conversation_name)
                if formatted_conv_name == bot.PHONE:
                    is_own_chat = True
                elif formatted_conv_name in bot.PHONES_LIST:
                    is_permitter_phone = True
            except:pass
            
            print("Noti except conditions:", not is_permitter_phone and not is_own_chat)
            if (not is_permitter_phone and not is_own_chat):
                continue
            
            # Ingresar al chat
            bot.CURRENT_CHAT = {}
            #parent = get_parent(n)
            done = None
            while not done:
                print(f"Parent class: {parent.get_attribute('class')}, {parent.get_attribute('data-testid')}, {parent.get_attribute('role')}")
                parent.click()
                time.sleep(0.2)
                if get_element(parent=driver, selector=selectors["chat_name"]):
                    done = True

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
        first_msg = get_next_msg(driver, selectors)

        if first_msg:
            if bot.START_MSG_CODE in first_msg.text and bot.CHATTER_CODE in first_msg.text:
                response = get_msg_data_id(first_msg)
                done = True
            else:
                last_msg = first_msg
        else:
            done = True

        # Obtener todos los mensajes nuevos
        print("Revisando mensajes siguientes...")
        while not done and not response:
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

def write_and_send(driver, selectors, input_element, message):
    has_new_input_id = True

    if has_new_input_id:
        act = ActionChains(driver)
        act.click(input_element)

        # Manejo del clipboard
        text = message.replace(':f:', "") + f':{bot.PHONE}:'
        while pyperclip.paste() != text:
            print(f"Esperando {bot.SLEEP_TIME} segundos")
            time.sleep(bot.SLEEP_TIME)
            while not f":{bot.PHONE}:" in pyperclip.paste():
                wait_and_set(text, bot.CLIPBOARD_SLEEP_TIME)    
        
        # Pegar mensaje
        act.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
        time.sleep(0.5)

        # Limpiar código y liberar clipboard
        act.click(input_element)
        time.sleep(0.5)
        act.key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL)
        act.send_keys(Keys.BACKSPACE)
        for d in bot.PHONE:
            act.send_keys(Keys.BACKSPACE)
        act.send_keys(Keys.BACKSPACE)
        act.perform()
        release_clipboard()
    else:
        driver.execute_script("let txt = arguments[0].innerText; arguments[0].innerText = txt + `{}`".format(message), input_element)
        input_element.send_keys('.')
        input_element.send_keys(Keys.BACKSPACE)
    
    time.sleep(0.5)

    # Enviar mensaje
    input_element.send_keys(Keys.ENTER)
    time.sleep(2)
    print("Mensaje enviado")

def locate_msg_element(driver, selectors, msg_id):
    reference_elem = None
    is_cached = False

    if not reference_elem:
        try:
            reference_elem = get_element(parent=driver, selector=f'//div[@data-id="{msg_id}"]')
            is_cached = True
        except:pass

        if is_cached:
            set_focusable_item_class(reference_elem, driver, selectors)
            
    return reference_elem

def read_chat(driver, selectors, chat_name, type='group'):
    success = False
    open_needed = True
    chat_ready = False
    try:
        chat_header = get_element(driver, selectors["chat_header"])
        chat_name_header = get_element(chat_header, selectors["chat_name_header"])
        print('Chat name: ', chat_name_header.text)
        
        open_needed = chat_name_header.text != chat_name
    except:pass
    
    if open_needed:
        message_input = open_chat(driver, selectors, celular=chat_name, init=False)
        chat_ready = message_input != None
    else:
        chat_ready = True

    if chat_ready and type == 'group':
        reference_message = get_next_msg(driver, selectors) if bot.ACTUAL_READED_MSG == "" else get_next_msg(driver, selectors, actual_msg_id=bot.ACTUAL_READED_MSG)

        if reference_message:
            reference_id = get_msg_data_id(reference_message)
            success = response_group_msg(driver, selectors, actual_msg=reference_message, group_name=chat_name)
            if success:
                bot.ACTUAL_READED_MSG = reference_id
    
    return success

def response_group_msg(driver, selectors, actual_msg, group_name):
    result = False
    reference_id = get_msg_data_id(actual_msg)

    print("Intentando abrir menu contextual")
    actual_msg.send_keys(Keys.ARROW_RIGHT)
    done = None
    while not done:
        try:
            click_element(actual_msg, selectors["download_options"])
            done = True
        except:
            time.sleep(0.5)
            webdriver.ActionChains(driver).send_keys(Keys.ARROW_RIGHT).perform()
    
    private_chat_oppened = False
    try:
        time.sleep(2)
        click_element(driver, selectors["private_reply"])
        private_chat_oppened = True
    except:pass

    if private_chat_oppened:
        time.sleep(1)
        input_element = get_input(driver, selectors, key="message")

        write_and_send(driver, selectors, input_element, message=f'{bot.RESPONSE_MSG} _(cttr)_')

        result = back_to_group(driver, selectors)

    return result

def back_to_group(driver, selectors):
    result = False
    last_send = None

    sleep_counter = 0
    done = None
    while (not done) and (sleep_counter < 15):
        try:
            last_send = get_elements(driver, selectors["message_out_container"], method='css')[-1]
            if last_send:
                done = True
            else:
                raise Exception("No se pudo recuperar wa_id")
        except Exception as e:
            print(e)
            time.sleep(1)
            sleep_counter = sleep_counter + 1
    
    if last_send:
        print(last_send.get_attribute("class"))
        try:
            # Click en mención
            quote = get_element(last_send, selectors["quoted_message"])

            click_element(quote, ".//div[@role='button']")
            result = True
        except Exception as e:
            print(e)

    return result

def get_next_msg(driver, selectors, actual_msg_id=None):
    result = None
    first_msg = None
    
    is_unread = False
    is_from_outbound = False
    is_first_msg = False

    # Cached message
    reference_elem = locate_msg_element(driver, selectors, msg_id=actual_msg_id)
    if reference_elem:
        reference_elem.send_keys(Keys.ARROW_DOWN)
        reference_elem = driver.switch_to.active_element
        is_same = False if get_msg_data_id(reference_elem) != actual_msg_id else True
        if is_same:
            reference_elem.send_keys(Keys.ARROW_DOWN)
            reference_elem = driver.switch_to.active_element

        is_chat_separator = False
        for selector in selectors["chat_separator_class"]:
            if selector in reference_elem.get_attribute("class"):
                is_chat_separator = True
                break
        print(f"Es un separador de chat: {'SI' if is_chat_separator else 'NO'}")

        if is_chat_separator:
            reference_elem.send_keys(Keys.ARROW_DOWN)
            reference_elem = driver.switch_to.active_element

        if selectors["message_out_class"] in reference_elem.get_attribute("class"):
            message_out_container = get_elements(driver, selectors["message_out_container"], method='css')[-1]
            if message_out_container:
                reference_elem = message_out_container
                set_tabindex(reference_elem, driver, selectors)
                reference_elem.send_keys(Keys.ARROW_DOWN)
                reference_elem = driver.switch_to.active_element

    else:
        # Unread message
        reference_elem = get_element(parent=driver, selector=selectors["unread"])
        if reference_elem:
            is_unread = True
        
        if is_unread:
            reference_elem.click()
            reference_elem.send_keys(Keys.ARROW_DOWN)
            reference_elem = driver.switch_to.active_element
            if bot.SHOW_EX_PRINTS:
                print("Hay mensajes no leidos")

        # From last outbound
        if not reference_elem:
            try:
                reference_elem = get_elements(parent=driver, selector=selectors["message_out_container"], method='css')[-1]
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
                reference_elem = get_elements(parent=driver, selector=selectors["message_in_container"], method='css')[0]
                is_first_msg = True
            except:pass

            if is_first_msg:
                set_tabindex(reference_elem, driver, selectors)
                first_msg = reference_elem
                if bot.SHOW_EX_PRINTS:
                    print("Obteniendo primer mensaje entrante del chat")

    if not first_msg and reference_elem:
        set_tabindex(reference_elem, driver, selectors)
        first_msg = reference_elem

        # Comprobar si es el mensaje de "este chat está cifrado"
        try:
            get_elements(parent=first_msg, selector=selectors["encrypted_chat"])[-1] 
            first_msg.send_keys(Keys.ARROW_DOWN)
            first_msg = driver.switch_to.active_element
        except:pass
        # Comprobar si es el mensaje de "mensajes temporales"
        try:
            get_elements(parent=first_msg, selector=selectors["temporal_chat"])[-1] 
            first_msg.send_keys(Keys.ARROW_DOWN)
            first_msg = driver.switch_to.active_element
        except:pass


        # Buscar primer mensaje
        is_notification = True
        while not get_msg_data_id(first_msg) and is_notification:
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
            
            is_notification = False
            if get_element(first_msg, selectors["invite_notification"]): # Revisar si es notificacion "se unió usando el enlace de invitacion"
                is_notification = True
            time.sleep(1)

            if is_chat_item or is_unread_sign or is_notification:
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
            elif not is_chat_item: # Si no es elemento del chat TAB hasta entrar a la ventana del chat
                first_msg.send_keys(Keys.TAB)
                first_msg = driver.switch_to.active_element
                time.sleep(0.5)
            
            # Comprobar si es el mensaje de "este chat está cifrado"
            if get_element(parent=first_msg, selector=selectors["encrypted_chat"]):
                set_tabindex(first_msg, driver, selectors)
                first_msg.send_keys(Keys.ARROW_DOWN)
                first_msg = driver.switch_to.active_element
        time.sleep(1)

    if first_msg:
        print("Mensaje obtenido")

        # Condiciones
        not_msg_out = ('false' in get_msg_data_id(first_msg)) if get_msg_data_id(first_msg) else False

        print(f"Es un mensaje nuevo: {'SI' if (not_msg_out) else 'NO'}")

        if not_msg_out:
            if get_msg_data_id(first_msg) != actual_msg_id:
                result = first_msg

    return result