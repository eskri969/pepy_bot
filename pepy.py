#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging
import sh
import json
from time import sleep

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PERMINIT, NOMBRE, DNI, CLUB, ACTIVIDAD, TELEFONO, EDIFICIO, DEPENDENCIA, FECHA, HENTRADA, HSALIDA, SUMMARY, MAIL = range(13)
form=open("permisodeAula.json","r")
request_data = json.load(form)
secret=open("secret.json","r")
passw = json.load(secret)
filled_file=""

def exit(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Pues adios! si algún dia me necesitas, '
                                'ya sabes donde estoy.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def start(bot, update):
    reply_keyboard = [['Nuevo Permiso de Aulas', 'Nuevo Permiso de Aulas']]
    user ="@"+update.message.from_user.username
    if user =="@":
            user = update.message.from_user.first_name
    logger.info("User %s started the conversation.", user)
    update.message.reply_text(
        'Hola '+user+',\nmi nombre es Pepy y he sido creada para ayudar en el papeleo'
        'de la ETSIT.\nUsa /exit para parar esta conversacion en cualquier momento.'
        'podrás volver a hablarme usando /start :).'
        '\nUsa /cancel para parar cualquier papeleo que esté a medias.'
        '\n\n ¿Que quieres hacer?.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return PERMINIT

def cancel(bot, update):
    print("cancel")
    reply_keyboard = [['Nuevo Permiso de Aulas', 'Nuevo Permiso de Aulas']]
    update.message.reply_text(
        'Vale pues hacemos como si esto nunca hubiese pasado.\n\n ¿Que quieres hacer?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return PERMINIT

def permInit(bot, update):
    update.message.reply_text(
        'Vale!\nSoy una experta en esto, pero necesito que me respondas un par de'
        ' cosas para rellenarlo. Todo lo que escribas ahora estará tal cual en el'
        'permiso, así que cuidadito ;).',
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('¿Cual es tu nombre y apellidos?')

    return NOMBRE

def nombre(bot, update):
    request_data["(Nombre)"]=update.message.text
    update.message.reply_text('Dime tu DNI',reply_markup=ReplyKeyboardRemove())
    return DNI

def dni(bot, update):
    request_data["(DNI)"]=update.message.text
    update.message.reply_text('¿Cual es tu club?',reply_markup=ReplyKeyboardRemove())
    return CLUB

def club(bot, update):
    request_data["(Club)"]=update.message.text
    update.message.reply_text('¿Para qué actividad es el permiso?',reply_markup=ReplyKeyboardRemove())
    return ACTIVIDAD

def actividad(bot, update):
    request_data["(Actividad)"]=update.message.text
    update.message.reply_text('Dime tu teléfono movil',reply_markup=ReplyKeyboardRemove())
    return TELEFONO

def telefono(bot, update):
    request_data["(Telefono)"]=update.message.text
    update.message.reply_text('¿En que edificio está el aula?',reply_markup=ReplyKeyboardRemove())
    return EDIFICIO

def edificio(bot, update):
    request_data["(Edificio)"]=update.message.text
    update.message.reply_text('¿Qué aula es la que quieres?',reply_markup=ReplyKeyboardRemove())
    return DEPENDENCIA

def dependencia(bot, update):
    request_data["(Dependencia)"]=update.message.text
    update.message.reply_text('¿Qué día la necesitas?, Por favor indica día y mes.'
    ,reply_markup=ReplyKeyboardRemove())
    return FECHA

def fecha(bot, update):
    request_data["(Fecha)"]=update.message.text
    update.message.reply_text('¿Desde qué hora?',reply_markup=ReplyKeyboardRemove())
    return HENTRADA

def hentrada(bot, update):
    request_data["(HEntrada)"]=update.message.text
    update.message.reply_text('¿Hasta qué hora?',reply_markup=ReplyKeyboardRemove())
    return HSALIDA

def hsalida(bot, update):
    request_data["(HSalida)"]=update.message.text
    s=""
    for x in request_data.keys():
        s+=(x+" : "+request_data[x]+"\n")
    s=s.replace("(","")
    s=s.replace(")","")
    update.message.reply_text('Esto me has pedido:\n'+s,
    reply_markup=ReplyKeyboardRemove())
    reply_keyboard = [['Si', 'No']]
    update.message.reply_text('¿Todo bien?, si no lo esta volvemos a empezar',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SUMMARY


def summary(bot, update):
    #make .json again and execute backend.py
    print(request_data)
    global filled_file
    filled_file=(request_data["(Club)"]+"-"+request_data["(Edificio)"]+""+
                request_data["(Dependencia)"]+"-"+request_data["(Fecha)"]+"-"
                +request_data["(Nombre)"]).replace(" ","_").replace("/","-")
    f = open(filled_file+".json","w")
    json.dump(request_data,f)
    f.close()
    sh.python("backend.py",filled_file+".json",filled_file+".pdf")
    update.message.reply_text('Pues en cuanto me des tu email te lo mando.'
    ,reply_markup=ReplyKeyboardRemove())
    return MAIL

def mail(bot, update):
    if update.message.text.lower() == "pepi@etsit.upm.es" :
         update.message.reply_text('No es muy buena idea hacer eso, será mejor'
         'que primero lo recibas en tu bandeja de correo y luego se lo envíes'
         'a la persona que le corresponda ;).\n Ahora dame tu email y te lo mando'
         ,reply_markup=ReplyKeyboardRemove())
         return MAIL

    sh.python("mailsender.py",update.message.text,filled_file+".pdf")
    sh.rm(filled_file+".pdf",filled_file+".json")
    reply_keyboard = [['Nuevo Permiso de Aulas', 'Nuevo Permiso de Aulas']]
    update.message.reply_text('¿Que quieres hacer ahora?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return PERMINIT


def rest(bot, update):
    reply_keyboard = [['Nuevo Permiso de Aulas', 'Nuevo Permiso de Aulas']]
    update.message.reply_text(
        '¿Que quieres hacer ahora?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return PERMINIT

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(passw["token"])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            PERMINIT: [RegexHandler('^(Nuevo Permiso de Aulas|Nuevo Permiso de Aulas)$', permInit)],

            NOMBRE: [MessageHandler(Filters.text, nombre)],

            DNI: [MessageHandler(Filters.text, dni)],

            CLUB: [MessageHandler(Filters.text, club)],

            ACTIVIDAD: [MessageHandler(Filters.text, actividad)],

            TELEFONO: [MessageHandler(Filters.text, telefono)],

            EDIFICIO: [MessageHandler(Filters.text, edificio)],

            DEPENDENCIA: [MessageHandler(Filters.text, dependencia)],

            FECHA: [MessageHandler(Filters.text, fecha)],

            HENTRADA: [MessageHandler(Filters.text, hentrada)],

            HSALIDA: [MessageHandler(Filters.text, hsalida)],

            SUMMARY: [RegexHandler('^(Si)$', summary),
                      RegexHandler('^(No)$', rest)],

            MAIL: [MessageHandler(Filters.text, mail)],


        },

        fallbacks=[CommandHandler('exit', exit),
                   CommandHandler('cancel',cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
