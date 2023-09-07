# Packages
import time, pyperclip

# Application
import bot

# Webdriver
from selenium.webdriver.remote.webdriver import By

# Clipboard
def wait_and_set(text, clipboard_sleep_time):
    clip_text = pyperclip.paste()
    while not ":f:" in clip_text:
        print(f"Esperando clipboard {clipboard_sleep_time} segundos")
        time.sleep(clipboard_sleep_time)
        release_clipboard()
        clip_text = pyperclip.paste()
    pyperclip.copy(text)

def release_clipboard():
    text = pyperclip.paste()
    # Condiciones
    is_bot_text = (f":{bot.PHONE}:" in text)
    is_empty_str = (len(text) == 0)
    
    if is_empty_str:
        is_any_bot_text = True
    else:
        is_any_bot_text = (text[len(text) - 1] == ":" and len(text.split(':')) > 2)

    if is_bot_text or is_empty_str or not(is_any_bot_text):
        print(is_bot_text, is_empty_str, is_any_bot_text)
        if text == pyperclip.paste():
            print("Liberando clipboard, texto: ", pyperclip.paste())
            pyperclip.copy(':f:')

# Manejo de elementos
def get_parent(element):
    return element.find_element(By.XPATH, '..')

def get_elements(parent, selector, method='xpath', first=False):
    elem = None
    func = By.XPATH if method == 'xpath' else By.CSS_SELECTOR
    if type(selector) == list:
        for s in selector:
            elem = parent.find_elements(func, s)
            if len(elem) == 0:
                elem = None
            else:
                if first:
                    elem = elem[0]
                break
    else:
        elem = parent.find_elements(func, selector)
        if len(elem) == 0:
            elem = None
        else:
            if first:
                elem = elem[0]

    key = [i for i in bot.SELECTORS if bot.SELECTORS[i]==selector]
    key = key[0] if key else selector
    cant = len(elem) if elem and not first else 0
    print(f'"{key}" by {method}: {"SI" if elem else "NO"} {"(first)" if first else f"({cant})"}')
    
    return elem

def get_element(parent, selector, method='xpath'):
    return get_elements(parent=parent, selector=selector, method=method, first=True)

def click_element(parent, selector, method='xpath'):
    done = False
    try:
        get_element(parent=parent, selector=selector, method=method).click()
        done = True
    except:pass
    key = [i for i in bot.SELECTORS if bot.SELECTORS[i]==selector]
    key = key[0] if key else selector
    print(f'Clicked "{key}": {"OK!" if done else "FAIL!"}')

    return done

# Manejo de chats  
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