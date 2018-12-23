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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

REST,PERMINIT, NOMBRE, DNI, CLUB, ACTIVIDAD, TELEFONO, EDIFICIO, DEPENDENCIA, FECHA, HENTRADA, HSALIDA, SUMMARY, MAIL = range(14)


def start(bot, update):
    reply_keyboard = [['Nuevo Permiso de Aulas', 'Nuevo Permiso de Aulas']]
    print("start")

    update.message.reply_text(
        'Hola mi nombre es Pepy y he sido creada para ayudar en el papeleo'
        'de la ETSIT.\n\n ¿Que quieres hacer?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return PERMINIT

def permInit(bot, update):
    update.message.reply_text(
        'Vale!\nSoy una experta en esto, pero necesito que me respondas un par de'
        ' cosas para rellenarlo. Todo lo que escribas ahora estará tal cual en el'
        'permiso, así que cuidadito ;).',
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('¿Cual es tu NOMBRE?')

    return NOMBRE

def nombre(bot, update):
    update.message.reply_text('¿Dime tu DNI?',reply_markup=ReplyKeyboardRemove())
    return DNI

def dni(bot, update):
    update.message.reply_text('¿Cual es tu CLUB?',reply_markup=ReplyKeyboardRemove())
    return CLUB

def club(bot, update):
    update.message.reply_text('¿Para qué actividad es el permiso?',reply_markup=ReplyKeyboardRemove())
    return ACTIVIDAD

def actividad(bot, update):
    update.message.reply_text('¿Dime tu teléfono?',reply_markup=ReplyKeyboardRemove())
    return TELEFONO

def telefono(bot, update):
    update.message.reply_text('¿En que edificio está el aula?',reply_markup=ReplyKeyboardRemove())
    return EDIFICIO

def edificio(bot, update):
    update.message.reply_text('¿Qué aula es la que quieres?',reply_markup=ReplyKeyboardRemove())
    return DEPENDENCIA

def dependencia(bot, update):
    update.message.reply_text('¿Qué día la necesitas?',reply_markup=ReplyKeyboardRemove())
    return FECHA

def fecha(bot, update):
    update.message.reply_text('¿Desde qué hora?',reply_markup=ReplyKeyboardRemove())
    return HENTRADA

def hentrada(bot, update):
    update.message.reply_text('¿Hasta qué hora?',reply_markup=ReplyKeyboardRemove())
    return HSALIDA

def hsalida(bot, update):
    update.message.reply_text('Esto me has pedido:\n-\n-\n-\n-\n-\n-\n',
    reply_markup=ReplyKeyboardRemove())
    reply_keyboard = [['Si', 'No']]
    update.message.reply_text('Todo bien o volvemos a empezar',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SUMMARY


def summary(bot, update):
    update.message.reply_text('pues dejame tu mail y te lo mando en un momen'
    ,reply_markup=ReplyKeyboardRemove())
    return MAIL


def rest(bot, update):
    reply_keyboard = [['Nuevo Permiso de Aulas', 'Nuevo Permiso de Aulas']]
    print("start")

    update.message.reply_text(
        'Pues esto ya esta termniando.\n\n ¿Que quieres hacer?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return PERMINIT

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("TOKEN")

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

            SUMMARY: [RegexHandler('^(Si|No)$', summary)],

            MAIL: [MessageHandler(Filters.text, rest)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
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
