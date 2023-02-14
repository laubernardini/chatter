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
    args = parser.parse_args()

    if args.celular:
        phone = args.celular
        if phone and phone != "":
            bot.PHONE = phone
            bot.calc_sleeptime()
            bot.MESSAGE = f"Hola! Soy chatter _*{bot.PHONE}*_"

    print(f"PHONE: {bot.PHONE}")
    system("title CHATTER " + bot.PHONE)
        
    start()

run()