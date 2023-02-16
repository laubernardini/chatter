# Datos del bot
PHONE = ""
VERSION = "1.0"

# Variables de ejecución
OS_SLASH = "\\" # / -> linux \\ -> windows
BROWSER = "chrome"
DRIVER_PATH = "chromedriver.exe"#"/usr/local/bin/chromedriver"#
START_DATE = None
FORCED_ACTIVITY_FREQUENCY = 5 # En minutos. Click para marcar al navegador como "activo" frente al SO 
MESSAGE = ""

# Log
SHOW_ERRORS = True
SHOW_API_RESPONSES = True
SHOW_EX_PRINTS = True

# Cache
NEXT_FORCED_ACTIVITY = None
SLEEP_TIME = 0
CLIPBOARD_SLEEP_TIME = 0
GROUPS_LIST = []

def calc_sleeptime():
    global PHONE, SLEEP_TIME, CLIPBOARD_SLEEP_TIME

    sleep_time = float(int(PHONE) / 10)
    while sleep_time > 3:
        sleep_time /= 2
    SLEEP_TIME = sleep_time
    CLIPBOARD_SLEEP_TIME = (sleep_time if sleep_time < 3 else sleep_time / 2) if (sleep_time > 1) else (sleep_time + 1)
