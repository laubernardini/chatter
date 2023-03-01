# Packages
import argparse
from os import system

# Application
import bot
from main import start

# Functions
def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--bot", help="Bot PK")
    parser.add_argument("-c", "--celular", help="Celular")
    parser.add_argument("-s", "--server", help="Server")
    parser.add_argument("-br", "--browser", help="Browser")
    parser.add_argument("-d", "--desc", help="Descripcion")
    args = parser.parse_args()

    if args.celular:
        phone = args.celular
        if phone and phone != "":
            bot.PHONE = phone
            bot.calc_sleeptime()
            bot.MESSAGE = f"Hola! Soy chatter _*{bot.PHONE}*_"
    if args.server == 'cat' or args.server == 'CAT':
        bot.SERVER_URL = "https://cat-technologies.apicloud.com.ar"
    if args.desc:
        bot.DESCRIPCION = args.desc
        print(f'Desc: {bot.DESCRIPCION}')

    print(f"PHONE: {bot.PHONE}")
    system("title CHATTER " + bot.PHONE)
        
    start()

run()