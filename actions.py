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
        if text != bot.PHONE:
            result = True
        else:
            try:
                chat_header = driver.find_element_by_xpath(selectors["chat_header"])
                try:
                    chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header"])
                except:
                    chat_name_header = chat_header.find_element_by_xpath(selectors["chat_name_header_1"])
                    
                if chat_name_header.text == text:
                    result = True
            except:pass
        
    return result

def open_chat(driver, selectors, celular):
    elem = None
    elem = search(driver, selectors, celular)
        
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
    
    return elem

def send_message(mensaje="", celular="", driver=None, selectors=None):
    try:
        elem = open_chat(driver, selectors, celular)
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
    except Exception as e:
        if bot.SHOW_ERRORS:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Error enviando mensaje")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
            print(os.path.split(exc_tb.tb_frame.f_code.co_filename)[1], ", linea ", exc_tb.tb_lineno)
