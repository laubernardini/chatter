from os import system
import bot, sys

from main import start, raise_phone_error, send_report

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-b","--bot", help="Bot PK")
parser.add_argument("-c", "--celular", help="Celular")
parser.add_argument("-s", "--server", help="Server")
parser.add_argument("-br", "--browser", help="Browser")
args = parser.parse_args()

if args.bot:
    bot.BOT_PK = args.bot
if args.celular:
    phone = args.celular
    if phone and phone != "":
        bot.PHONE = phone
if args.server == 'cat' or args.server == 'CAT':
    bot.SERVER_URL = "https://cat-technologies.apicloud.com.ar/thread-"
    bot.FILE_SERVER = "https://cat-technologies.apicloud.com.ar"
    bot.FILE_SERVER_2 = "http://cat-technologies.apicloud.com.ar:8080"
if args.browser:
    bot.BROWSER = "firefox" if args.browser == 'f' else ("opera" if args.browser else "chrome")

bot.VERSION = "3.0"
print(f"PK: {bot.BOT_PK}, PHONE: {bot.PHONE}")

sleep_time = float(int(bot.BOT_PK) / 10)
while sleep_time > 5:
    sleep_time /= 2
bot.SLEEP_TIME = sleep_time
bot.CLIPBOARD_SLEEP_TIME = (sleep_time if sleep_time < 3 else sleep_time / 2) if (sleep_time > 1) else (sleep_time + 1)

bot.DOWNLOAD_PATH = bot.DOWNLOAD_PATH + str(bot.BOT_PK) + bot.OS_SLASH

system("title BOT " + bot.BOT_PK)

send_report()
if bot.PHONE != "":
    if bot.REGISTERED_PHONE != 'ALL' and bot.REGISTERED_PHONE != bot.PHONE:
        raise_phone_error(error='phone')
    
start()