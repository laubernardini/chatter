import asyncio
from os import system
import bot
import getopt
import sys

from main import start
from apis import status

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, 'b:c', ['foperand', 'soperand'])
if len(opts) == 0:# or len(opts) > 1:
    print ('Falta un parámetro: -b <BOT_PK>')
    #exit()
else:
    bot.BOT_PK = opts[0][1]
    if len(opts) == 2:
        try:
            phone = opts[1][1]
            if phone and phone != "":
                bot.PHONE = phone
        except:
            pass
    bot.VERSION = "3.0"
    print(f"PK: {bot.BOT_PK}, PHONE: {bot.PHONE}")

bot.DOWNLOAD_PATH = bot.DOWNLOAD_PATH + str(bot.BOT_PK) + bot.OS_SLASH

system("title BOT " + bot.BOT_PK)

asyncio.run(status())
start()