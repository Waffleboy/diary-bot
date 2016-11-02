# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 15:24:24 2016

@author: waffleboy
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,ConversationHandler
import messageProcessor as mp
import os,threading
from flask import Flask
import logger_settings
import signupFlow
import dbWrapper

HEROKU = True #If deploying on heroku.

TARGET_EMAIL, MY_EMAIL, APP_KEY = range(3)

# Enable logging
logger = logger_settings.setupLogger().getLogger(__name__)

#==============================================================================
#                               SLASH COMMANDS
#==============================================================================

# These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def log(bot, update):
    username = update.message.from_user.username
    telegram_id = update.message.from_user.id
    update.message.reply_text("Processing..")
    logger.info("Got a message from %s",username)
    user = dbWrapper.getUserFromTelegramID(telegram_id)
    
    if not user:
        update.message.reply_text("Hey %s, I'd love to help you but you're not registered! Type /register to register!",username)
        return
    messageToSave = update.message.text
    success = mp.processMessage(messageToSave,"diaryLog",user,update)
    if success:
        update.message.reply_text("Message has been sent to your specified emails!")
        return
    update.message.reply_text("Unfortunately an error has occured - Contact @waffleboy")

def accountStatus(bot,update):
    logger.info("Received request for account status from user %s",update.message.from_user.username)
    telegram_id = update.message.from_user.id
    update.message.reply_text("Processing..")
    user = dbWrapper.getUserFromTelegramID(telegram_id)
    if user:
        try:
            username = user.username
            username = str(username)
            email = user.getMyEmail()
            usage = str(user.times_used)
            
            targetEmails = stringify(user.getTargetEmails())
            update.message.reply_text("Hey "+str(username) + 
            ", your current email is "+str(email) +", recipient emails are: "+ targetEmails + " and you have used us "
            + usage + " times.")
        except Exception as e:
            logger.warn("Error occured in account status - %s",update.message.from_user.username)
            logger.exception(e)
            update.message.reply_text("I'm sorry, an error occurred accessing the database. Contact @waffleboy for help")
        return
    update.message.reply_text("You are currently not a registered user. Type /register to sign up now!")
    
def help(bot, update):
    update.message.reply_text(getHelpText())

def deleteAccount(bot,update):
    username = update.message.from_user.username
    logger.info("Got a request to delete account by user %s",username)
    update.message.reply_text("Processing...")
    user = dbWrapper.getUserFromTelegramID(update.message.from_user.id)
    if user:
        result = dbWrapper.deleteUser(user)
        if result:
            logger.info("Successfully deleted user %s",username)
            update.message.reply_text("Okay, I've deleted you from my records. I will miss you %s!",username)
            return
        update.message.reply_text("Could not delete you from my system - Contact @waffleboy for help")
        return
    update.message.reply_text("You're already not a registered user! Why not try signing up?" )
    
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    
def start(bot, update):
    update.message.reply_text("""
    Welcome to DiaryBot!
    
DiaryBot helps you log messages to the emails specified by you, all from the convenience of telegram!
    
Type '/register' to signup if you're a new user, else type /log <message here> to begin!
""")

#==============================================================================
#                               Helper Funcs
#==============================================================================

def getHelpText():
    s = """If you've not registered, use /register to register.
    
Use /log <message> to send the email to the specified emails in your account.

Use /accountstatus to check details about your account.

Use /deleteaccount to delete your account.
    
For further help, contact @waffleboy
"""
    return s

# Version 0.1 - NOT USED.
def userNotAuthorised(update):
    username = (update.message.from_user.username).lower().strip().rstrip()
    if (username == "waffleboy"):
        return False
    logger.info("Unauthorised user: %s",username)
    return True
    
#==============================================================================
#                                   Misc
#==============================================================================

# Standard reply upon texting the bot
def standardReply():
    s = "At the moment, I only reply to slash commands. Please try /help for more information!"
    return s

# Heroku bypass - not generally needed
def listenToPort():
    app = Flask(__name__)
    logger.info("Beginning Flask server to prevent shutdown by Heroku")
    app.run(debug=False,host = '0.0.0.0',port= int(os.environ.get('PORT', 33507)))

@app.route('/')
def standardPageOnHeroku():
    return "DiaryBot is now awake!"
    
def isProductionEnvironment():
    if os.environ.get('PRODUCTION'):
        return True
    return False
    
def getUpdater():
    if isProductionEnvironment():
        logger.info("Using Production key %s",os.environ.get("TELEGRAM_DIARYBOT_TOKEN"))
        return Updater(os.environ.get("TELEGRAM_DIARYBOT_TOKEN"))
    return Updater(os.environ.get("TELEGRAM_DIARYBOT_TEST_TOKEN"))

def stringify(emails):
    s = ''
    for entry in emails:
        s += entry +', '
    s = s[:-2]
    return s
#==============================================================================
#                                   Run
#==============================================================================
    
def main():
    logger.info("Starting Bot!")
    # Create the EventHandler and pass it your bot's token.
    updater = getUpdater()

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("log", log))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("accountstatus", accountStatus))
    dp.add_handler(CommandHandler("deleteaccount", deleteAccount))
    
    #add conv handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', signupFlow.register)],

        states={
            TARGET_EMAIL: [MessageHandler(Filters.text,
                                    signupFlow.target_email,
                                    pass_user_data=True)
                       ],

            MY_EMAIL: [MessageHandler(Filters.text,
                                           signupFlow.my_email,
                                           pass_user_data=True),
                            ],

            APP_KEY: [MessageHandler(Filters.text,
                                          signupFlow.one_time_password,
                                          pass_user_data=True),
                           ],
        },

        fallbacks=[CommandHandler('cancel', signupFlow.cancel,pass_user_data=True)]
    )

    dp.add_handler(conv_handler)
    
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
    if HEROKU:
        threading.Thread(target=listenToPort).start()
    main()