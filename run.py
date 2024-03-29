# Packages
import argparse
from os import system

# Application
import bot
from main import start

# Functions
def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--celular", help="Celular")
    parser.add_argument("-s", "--server", help="Server")
    parser.add_argument("-g", "--grupos", help="Grupos")
    parser.add_argument("-lg", "--lista_grupos", help="ListaGrupos")
    parser.add_argument("-t", "--tiempo", help="Tiempo")
    parser.add_argument("-tm", "--tiempo_modo", help="TiempoModo")
    parser.add_argument("-d", "--desc", help="Descripcion")
    parser.add_argument("-so", "--so", help="Sistema Operativo")
    args = parser.parse_args()
    print(args)
    print(args.so)
    if args.celular:
        phone = args.celular
        if phone and phone != "":
            bot.PHONE = phone
            bot.calc_sleeptime()
            bot.set_message()
    if args.server == 'cat' or args.server == 'CAT':
        bot.SERVER_URL = "https://cat-technologies.apicloud.com.ar"
    if args.desc:
        bot.DESCRIPCION = args.desc
        print(f'Desc: {bot.DESCRIPCION}')
    if args.grupos:
        bot.GROUPS_ONLY = "s" in args.grupos.lower()
    if args.lista_grupos:
        bot.GROUPS_LIST_SOURCE = int(args.lista_grupos) - 1
    if args.tiempo_modo:
        tiempo_modo = args.tiempo_modo.replace("min", "").replace("m", "")
        bot.MODE_CHANGE_TIME = int(tiempo_modo)
    if args.tiempo:
        tiempo = args.tiempo.replace("min", "").replace("m", "")
        bot.AWAIT_TIME = int(tiempo)
    if args.so:
        if args.so == 'linux':
            bot.OS_SLASH = "/" # / -> linux \\ -> windows
            bot.DRIVER_PATH = "/usr/local/bin/chromedriver"#"chromedriver.exe"#
            bot.BINARY = "/home/cris/dev/chrome/chrome/chrome"#"c:\cft\chrome.exe"#

    print(f"PHONE: {bot.PHONE}")
    system("title CHATTER " + bot.PHONE)
        
    start()

run()