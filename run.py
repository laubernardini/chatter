import asyncio
from os import system
import bot
import getopt
import sys

from main import start
from apis import status

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, 'b:', ['foperand'])
if len(opts) == 0 or len(opts) > 1:
    print ('Falta un parámetro: -b <BOT_PK>')
    #exit()
else:
    bot.BOT_PK = opts[0][1]
    bot.VERSION = "3.0"

bot.DOWNLOAD_PATH = bot.DOWNLOAD_PATH + str(bot.BOT_PK) + bot.OS_SLASH

system("title BOT " + bot.BOT_PK)

asyncio.run(status())
start()