# -*- coding: utf-8 -*-

'''
API documentation:
https://github.com/eternnoir/pyTelegramBotAPI#general-api-documentation
'''
# Import telebot API wrapper
import telebot

# Import aiohttp for webhook
from aiohttp import web
import ssl
import logging

# Imports for date handling
import datetime
import time

# Imports for Google Drive Sheet
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Imports for speech to text
import speech_recognition as sr
from ffmpy import FFmpeg
import requests
import subprocess

# Imports for IT
import os
import schedule
import threading


# xusta_BOT's TOKEN, provided by BOT Father to devve (only manager)
API_TOKEN = '670513417:AAGFYCR9wqSFR3sZmCqoODldSImbFFMF84A'

# Managers ids (devve, m0wer, ermo, Test group, Eurigram, Euri[IT])
admins_id = [681869593, 4338540, 239569637,
             -284930691, -1025910, -1001163379910]
managers = [681869593, 4338540, 239569637]
group_id = -1025910  # Eurigram
it_id = -1001163379910

# Initialize few variables and list for functions

# List of current guarripunto request
current_request = []
# Formatting mask for dates in Turnos de Basura Google's Sheet
datemask = "%d/%m/%Y"
# Spreadsheet linking
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Parameters for IT
servers = {'skynet': '138.100.31.232',
           'walle': '138.100.31.236',
           'null': '138.100.31.225',
           'thor': '138.100.31.230',
           'renaissance': '138.100.31.237'
           }
# Servers which should be on
should_on = ['skynet', 'walle', 'null', 'renaissance']


# WEBHOOK SETTINGS


"""
Why WEBHOOK:
We are using webhook instead of polling because it makes the Telegram API
call us with the requests, instead of us having to ask every x milisecons
to the Telegram API.
To do so, we need to define an IP host where Telegram API can call us and a
Port for Telegram API to comunicate.
"""

# Wehbook parameters
WEBHOOK_HOST = 'skynet.eurielec.etsit.upm.es'
WEBHOOK_PORT = 80  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # You may need to put the IP address

# Path to the ssl certificate
WEBHOOK_SSL_CERT = '/home/skynet/xusta_BOT/certs/cert.pem'
# Path to the ssl private key
WEBHOOK_SSL_PRIV = '/home/skynet/xusta_BOT/certs/key.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

# Define the logger
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Define the bot to call it later (reply messages, handle them, remove webhook)
bot = telebot.TeleBot(API_TOKEN)

# Define app as aiohttp web application
app = web.Application()

print("Initializating xusta_BOT!")


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)
print("Request handler started!")


app.router.add_post('/{token}/', handle)


# FUNCTIONS


# Funtion to authenticate into Turnos de basura sheet
# We need to call this funtion every so often becasue the auth caducates if not
def auth_spreadsheet():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'secreto.json', scope)
    client = gspread.authorize(credentials)
    global sheet
    sheet = client.open("Turnos basura").sheet1


# Creates a list of people in Turnos de basura to display in gprequest
def users_list():
    auth_spreadsheet()
    w = sheet.col_values(7)[1:]
    w.sort()
    return w


def scores_dict():
        auth_spreadsheet()
        w = sheet.col_values(7)[1:]
        y = sheet.col_values(6)[1:]
        z = dict(zip(w, y))
        print(z)
        return z


# We need a second function so it doesn't confuse the second layer sustract_gp
def users_list2():
    auth_spreadsheet()
    w = sheet.col_values(7)[1:]
    w.sort()
    y = [x+"." for x in w]
    return y


# Speech to text (converts english speech to text)
def stt(filename):
    r = sr.Recognizer()
    output = sr.AudioFile(filename)
    with output as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.record(source)
    text = r.recognize_google(audio, language="es-ES")
    print(text)
    return text


# Turns for taking the trash out
def find_turn():
    auth_spreadsheet()
    today = datetime.datetime.today()
    try:
        for i in range(10):
            try:
                print(i)
                days_back = datetime.timedelta(i)
                find = sheet.find((today-days_back).strftime(datemask))
                row = find.row
                name = sheet.cell(row, 1).value
                surname = sheet.cell(row, 2).value
                full_name = name + " " + surname
                print(find)
                if sheet.cell(row, 5).value == "done":
                        print(full_name + ", pero ya lo ha hecho!")
                        return "Le toca a " + full_name + " pero ya lo hizo"
                print("Le toca a", full_name)
                return "Le toca a " + full_name
            except Exception as e:
                print("Exception:", e)
                pass
    except Exception:
        return "I couldn't find a turn! Check the spreadsheet's date format"


# Check trash turn as done
def turn_done():
    auth_spreadsheet()
    today = datetime.datetime.today()
    try:
        for i in range(10):
            try:
                print(i)
                days_back = datetime.timedelta(i)
                find = sheet.find((today-days_back).strftime(datemask))
                row = find.row
                sheet.update_cell(row, 5, 'done')
                print("Turn done!")
                return "Well done!"
            except Exception as e:
                print("Exception:", e)
                pass
    except Exception:
        return "I couldn't mark it as done :("


# Creates a keyboard with a list
def make_keyboard(buttons_list):
    new_keyboard = telebot.types.ReplyKeyboardMarkup()
    print("TYPE: ", type(buttons_list))
    for n in range(0, len(buttons_list)):
        button1 = telebot.types.KeyboardButton(buttons_list[n])
        new_keyboard.add(button1)
    return new_keyboard


# Everyday function
def everyday():
    info = "Good morning \n "
    for key in servers:
        response = os.system("ping -c 1 " + servers[key])
        if response == 0:
            info += key + ' is up! \n '
        else:
            info += key + ' is down! \n '
            if key in should_on:
                bot.send_message(group_id,
                                 'Could someone turn ' + key + ' on, please?')
    bot.send_message(it_id, info)


def worker1():
    while True:
        schedule.run_pending()
        time.sleep(1)
        print("Daily is working")


t = threading.Thread(target=worker1)
t.start()

# FIX THIS
# Run everyday function
schedule.every().day.at("07:30").do(everyday)


# HANDLERS


# Introduce new users to the bot with the command /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """
Bienvenido, soy xusta_BOT! Te indico mis funciones: \n
/turn - indica a quien le toca sacar la basura \n
/turndone - marca el turno de basura como hecho \n
/gprequest - solicita un guarripunto \n
/gpclean - resta un guarripunto \n
/gpboard - muestra la tabla de guarripuntos \n
/gplist - mira los guarripuntos pendientes de aceptar \n
/gpaccept - acepta el primer gprequest de la lista \n
/gprefuse - borra el primer gprequest de la lista \n
/gpreset - resetea toda la lista de gprequest \n
/status - estado de los servidores y ordenadores \n
                        """)


# Cast a message from the BOT to Eurigram
@bot.message_handler(commands=['cast'])
def cast(message):
    if message.chat.id not in managers:
        return
    bot.send_message(group_id, message.text[6:])
    return

# Speech to text (handles audio, and transcripts it in english)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.
                        format(API_TOKEN, file_info.file_path))
    if file.status_code == 200:  # try 3 times
        ff = FFmpeg(
            # inputs={filename: None},
            # outputs={'output.wav': "-ar 8000 -y"}
            inputs={'pipe:0': None},
            outputs={'output.wav': "-ar 8000 -y"})
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        ff.cmd
        audio_wav, stderr = ff.run(input_data=file.content,
                                   stdout=subprocess.PIPE)
        filename = 'output.wav'
        bot.reply_to(message, stt(filename))
        return
    except Exception as e:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, e)
        return


# Speech to text (handles audio, and transcripts it in english)
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    file_info = bot.get_file(message.audio.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.
                        format(API_TOKEN, file_info.file_path))
    if file.status_code == 200:  # try 3 times
        ff = FFmpeg(
            # inputs={filename: None},
            # outputs={'output.wav': "-ar 8000 -y"}
            inputs={'pipe:0': None},
            outputs={'output.wav': "-ar 8000 -y"})
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        ff.cmd
        audio_wav, stderr = ff.run(input_data=file.content,
                                   stdout=subprocess.PIPE)
        filename = 'output.wav'
        bot.reply_to(message, stt(filename))
        return
    except Exception as e:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, e)
        return


# Let's user add a guarripunto request to the list
@bot.message_handler(commands=['gprequest'])
def display_users(message):
    cid = message.chat.id
    if cid not in admins_id:
        bot.send_message(cid, "Who dis?")
        return
    global users
    users = users_list()
    bot.send_chat_action(message.chat.id, 'typing')
    print("Processing gprequest")
    bot.reply_to(message, "Te he hablado! Elige a quien en @xusta_BOT")
    # Creates the keyboard with the users list (one row)
    bot.send_message(message.from_user.id, "Elige un usuario:",
                     reply_markup=make_keyboard(users))

    # Read users keyboard selection
    @bot.message_handler(func=lambda message:
                         message.text in users_list())
    def add_gp(message):
        global current_request
        # Removes keyboard
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        if message.text in current_request:
            bot.send_message(group_id,
                             "Lo siento, ya hay request pendiente para " +
                             message.text, reply_markup=markup)
            return
        bot.send_message(message.chat.id,
                         "GP solicitado a " + message.text,
                         reply_markup=markup)
        bot.send_message(group_id,
                         "@Ermosura se ha solicitado un GP a " +
                         message.text)
        current_request.append(message.text)
        return
    time.sleep(15)
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.from_user.id,
                     "Closing your keyboard in case you didn't answer",
                     reply_markup=markup)
    return


# Accepts a guarripunto request
@bot.message_handler(commands=['gpaccept'])
def accept_gp(message):
    auth_spreadsheet()
    global current_request
    print(current_request)
    if message.from_user.id in admins_id:
        if current_request == []:
            bot.reply_to(message, "No hay requests pendientes")
            return
        try:
            actual_user = current_request.pop(0)
            user_row = sheet.find(actual_user).row
            val = int(sheet.cell(user_row, 6).value)
            sheet.update_cell(user_row, 6, str(val+1))
            bot.reply_to(message, "Se ha sumado 1GP a " + actual_user)
            if int(sheet.cell(user_row, 6).value) == 3:
                bot.reply_to(message, actual_user + " ha llegado a 3gp!")
                return
            if int(sheet.cell(user_row, 6).value) >= 5:
                bot.reply_to(message, actual_user + " lleva 5 o más gp!")
                return
            return
        except Exception as e:
            print(e)
            bot.reply_to(message, "Something failed...")
            return
    else:
        bot.reply_to(message, "Madre mía tú, pero quién te crees payaso!")
        return


# Refuses a guarripunto request
@bot.message_handler(commands=['gprefuse'])
def refuse_gp(message):
    auth_spreadsheet()
    global current_request
    print(current_request)
    if message.from_user.id in admins_id:
        if current_request == []:
            bot.reply_to(message, "No hay requests pendientes")
            return
        try:
            actual_user = current_request.pop(0)
            bot.reply_to(message, "Request cancelado a " + actual_user)
            return
        except Exception as e:
            print(e)
            bot.reply_to(message, "Something failed...")
            return
    else:
        bot.reply_to(message, "Madre mía tú, pero quién te crees payaso!")
        return


@bot.message_handler(commands=['gpclean'])
def gpclean(message):
    cid = message.chat.id
    if cid not in managers:
        bot.send_message(cid, "Sorry not sorry")
        return
    global users
    users = users_list2()
    bot.send_chat_action(message.chat.id, 'typing')
    print("Processing gpclean")
    # Creates the keyboard with the users list (one row)
    bot.send_message(message.chat.id, "Elige un usuario:",
                     reply_markup=make_keyboard(users))

    # Read users keyboard selection
    @bot.message_handler(func=lambda message:
                         message.text in users_list2())
    def sustract_gp(message):
        # Removes keyboard
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id,
                         "GP restado a " + message.text,
                         reply_markup=markup)
        try:
            user_row = sheet.find(message.text[:-1]).row
            val = int(sheet.cell(user_row, 6).value)
            sheet.update_cell(user_row, 6, str(val-1))
            bot.reply_to(message, "Se ha restado 1GP a " + message.text[:-1])
            bot.send_message(group_id,
                             "Se ha restado 1GP a " + message.text[:-1])
            return
        except Exception as e:
            print(e)
            bot.reply_to(message, "Something failed...")
            return
        return
    time.sleep(15)
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.from_user.id,
                     "Closing your keyboard in case you didn't answer",
                     reply_markup=markup)
    return


# Returns the list of pending requests
@bot.message_handler(commands=['gplist'])
def list_gp(message):
    global current_request
    bot.reply_to(message, str(current_request))
    return


# Resets the list
@bot.message_handler(commands=['gpreset'])
def list_reset(message):
    global current_request
    if message.from_user.id in admins_id:
        current_request = []
        bot.reply_to(message, "Done, empty!")
        return
    else:
        bot.reply_to(message, "Madre mía tú, pero quién te crees payaso!")
        return


@bot.message_handler(commands=['gpboard'])
def score_board(message):
    bot.send_chat_action(message.chat.id, 'typing')
    guarros = {}
    victims = scores_dict()
    try:
        for key, value in victims.items():
            print(key + "   " + value)
            if int(value) != 0:
                guarros.update({key: int(value)})
        print(guarros)
        y = " \n ".join("{!s}: {!r}".format(key, val) for (key, val) in guarros.items())
        bot.reply_to(message, y)
        return
    except Exception as e:
        bot.reply_to(message, "Please wait 100s")
        print(e)
        # time.sleep(100)
        # score_board(message)
        return


# Handle /turn (gives the name of the person's turn)
@bot.message_handler(commands=['turn'])
def turno_basura(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        bot.reply_to(message, find_turn())
        return
    except Exception as e:
        print(e)
        bot.reply_to(message, "Issue at /turn handler")
        return


# Handle /turndone
@bot.message_handler(commands=['turndone'])
def marcar_hecho(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.id in admins_id:
        bot.reply_to(message, turn_done())
        return
    else:
        bot.reply_to(message, "Pero quién te crees puto inútil!")
        return


# Command to ping all servers and ask to turn importants on
@bot.message_handler(commands=['status'])
def status(message):
    bot.send_chat_action(message.chat.id, 'typing')
    for key in servers:
        response = os.system("ping -c 1 " + servers[key])
        if response == 0:
            bot.send_message(message.chat.id, key + ' is up!')
        else:
            bot.send_message(message.chat.id, key + ' is down!')
            if key in should_on:
                bot.send_message(group_id,
                                 'Could someone turn ' + key + ' on, please?')
    return


# SETUP WEBHOOK


# Remove webhook, it fails sometimes to set it if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context with certs and keys
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)


"""
Why aiohttp:
We are using aiohttp instead of flask cause it is starting to get obsolete.
Also, aiohttp has improved request's answer performance as you can see at
'y.tsutsumi.io/aiohttp-vs-multithreaded-flask-for-high-io-applications.html'
"""

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
