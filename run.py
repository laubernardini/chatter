import asyncio
from os import system
import bot
#import getopt
import sys

from main import start
from apis import status

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-b","--bot", help="Bot PK")
parser.add_argument("-c", "--celular", help="Celular")
args = parser.parse_args()

#argv = sys.argv[1:]
opts = []#, args = getopt.getopt(argv, 'b::c::', ['foperand'])
if args.bot:
    bot.BOT_PK = args.bot
if args.celular:
    phone = args.celular
    if phone and phone != "":
        bot.PHONE = phone
        
bot.VERSION = "3.0"
print(f"PK: {bot.BOT_PK}, PHONE: {bot.PHONE}")

bot.DOWNLOAD_PATH = bot.DOWNLOAD_PATH + str(bot.BOT_PK) + bot.OS_SLASH

system("title BOT " + bot.BOT_PK)

asyncio.run(status())
start()