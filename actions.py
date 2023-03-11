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

def open_chat(driver, selectors, celular, group):
    elem = None
    elem = search(driver, selectors, celular)

    if not group and not elem:
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

def send_message(mensaje="", celular="", driver=None, selectors=None, group=True):
    try:
        elem = open_chat(driver, selectors, celular, group)
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
