import os, shutil, urllib, urlfetch, pyperclip
from datetime import datetime, timedelta

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, json, actions, bot, main

import argparse

def wait_and_set(text, clipboard_sleep_time):
    while not ":f:" in pyperclip.paste() or pyperclip.paste() == "":
        print(f"Esperando clipboard {clipboard_sleep_time} segundos")
        time.sleep(clipboard_sleep_time)
    pyperclip.copy(text)

parser = argparse.ArgumentParser()
parser.add_argument("-t","--text", help="Text")
args = parser.parse_args()
b = args.text
text = f"BOT {b} 🧉 :{b}:"
sleep_time = float(int(b) / 10)
while sleep_time > 5:
    sleep_time /= 2
clipboard_sleep_time = (sleep_time if sleep_time < 3 else sleep_time / 2) if (sleep_time > 1) else (sleep_time + 1)


driver = main.driver_connect_chrome("https://google.com")
        
search = driver.find_element_by_name("q")


act = ActionChains(driver)

while pyperclip.paste() != text:
    while not f":{b}:" in pyperclip.paste():
        wait_and_set(text, clipboard_sleep_time)
    print(f"Esperando {sleep_time} segundos")
    time.sleep(sleep_time)

act.click(search)
act.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL)
print(search.text, b)

act.send_keys(Keys.BACKSPACE)
for d in b:
    act.send_keys(Keys.BACKSPACE)
act.send_keys(Keys.BACKSPACE)
act.perform()

pyperclip.copy(":f:")