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
    parser.add_argument("-t", "--tiempo", help="Tiempo")
    parser.add_argument("-d", "--desc", help="Descripcion")
    args = parser.parse_args()

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
    if args.tiempo:
        tiempo = args.tiempo.replace("min", "").replace("m", "")
        bot.AWAIT_TIME = int(tiempo)

    print(f"PHONE: {bot.PHONE}")
    system("title CHATTER " + bot.PHONE)
        
    start()

run()