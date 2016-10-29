# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 15:24:24 2016

@author: waffleboy
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import messageProcessor as mp
import os
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


#==============================================================================
#                               SLASH COMMANDS
#==============================================================================

# These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def log(bot, update):
    if userNotAuthorised(update):
        update.message.reply_text("Sorry, You're not authorised to use this Bot.")
        return
        
    messageToSave = update.message.text
    success = mp.processMessage(messageToSave,"diaryLog")
    if success:
        update.message.reply_text("Message has been sent!")
        return
    update.message.reply_text("Unfortunately an error has occured - Contact @waffleboy")
    
def help(bot, update):
    update.message.reply_text(getHelpText())

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    
def start(bot, update):
    update.message.reply_text("Type /log <message here> to begin!")

#==============================================================================
#                               Helper Funcs
#==============================================================================

def getHelpText():
    s = "Use '/log' to send an entry to email"
    return s

# #FIXME: Version 0.1
def userNotAuthorised(update):
    if (update.message.from_user.username.lower() != "waffleboy"):
        return False
    return True
    
#==============================================================================
#                              Misc & Run
#==============================================================================

# Standard reply upon texting the bot
def standardReply():
    s = "At the moment, I only reply to slash commands. Please try /help for more information!"
    return s
    
    
def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ["TELEGRAM_DIARYBOT_TOKEN"])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("log", log))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, standardReply()))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    print("Starting Bot!")
    main()