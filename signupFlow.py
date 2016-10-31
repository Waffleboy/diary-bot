# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 00:18:55 2016

@author: waffleboy
"""
from telegram.ext import ConversationHandler
from validate_email import validate_email
import yagmail
import dbWrapper,logger_settings
# Defined in diarybot.py, here only for reference.
TARGET_EMAIL, MY_EMAIL, APP_KEY = range(3)

logger = logger_settings.setupLogger().getLogger(__name__)


#==============================================================================
#                 Conversation Handler Functions - Signup Flow
#==============================================================================

def register(bot, update):
    logger.info("User %s with id %s began signup process",update.message.from_user.username,
                                                            update.message.from_user.id)
    update.message.reply_text("""
Allright! Firstly, what is/are the email address(es) that you wish to send logs to?
    
Seperate each email with a ','.
    
eg, abc@hotmail.com,potato@lol.com
""")
    return TARGET_EMAIL

def target_email(bot, update, user_data):
    text = update.message.text
    emailTexts = splitIfNecessary(text)
    
    if allAreValidEmails(emailTexts):
        update.message.reply_text('Got it. Now, what is your email address? (Gmail only!)')
        user_data['target_email'] = emailTexts
        return MY_EMAIL
    update.message.reply_text('That is not a valid email address. Try again, or type /cancel to cancel.')
    return TARGET_EMAIL

def my_email(bot,update,user_data):
    text = update.message.text
    if validEmail(text,gmail_needed=True):
        user_data['my_email'] = text
        update.message.reply_text("Okay, now please generate an Application-Specific password for use. \nVisit https://support.google.com/accounts/answer/185833?hl=en and select 'How to generate an App Password'.")
        update.message.reply_text("It looks like: ")        
        update.message.reply_photo("http://i.stack.imgur.com/Ekt0W.gif")
        update.message.reply_text("Once you have it, please key it in here (spaces not required)")
        return APP_KEY
    update.message.reply_text('That is not a valid email address. Try again, or type /cancel to cancel.')
    return MY_EMAIL

def one_time_password(bot,update,user_data):
    text = update.message.text
    if validPassword(user_data["my_email"],text):
        update.message.reply_text("Saving your details...")
        user_data['app_key'] = text
        user_data["telegram_id"] = update.message.from_user.id
        user_data["username"] = update.message.from_user.username
        if dbWrapper.signUpUser(user_data,update):
            update.message.reply_text("Hurray you're done! Just use /log and you're ready to go!")
        else:
            update.message.reply_text("An error occured in saving your details. Please contact @waffleboy for help")
        return ConversationHandler.END
    update.message.reply_text('That is not a valid application password. Authentication with Google failed. Try again, or type /cancel to cancel.')
    return APP_KEY


def cancel(bot, update,user_data):
    username = update.message.from_user.username
    logger.info("User %s cancelled registration process",username)
    user_data.clear()
    update.message.reply_text('Okay, your registration has been cancelled. Sad to see you go! :(')
    return ConversationHandler.END

#==============================================================================
#                               Misc Funcs
#==============================================================================

def splitIfNecessary(email_text):
    if ',' in email_text:
        return email_text.split(',')
    return [email_text]
    
def allAreValidEmails(email_list):
    emailsValid = True if sum([validEmail(email) for email in email_list]) == len(email_list) else False
    return emailsValid
    
def validEmail(email_add,gmail_needed=False):
    valid_status = validate_email(email_add)
    if not gmail_needed:
        return valid_status
    if valid_status and gmail_needed:
        return isDomainGmail(email_add)
    return False

def isDomainGmail(email_add):
    domain = email_add[email_add.find('@'):]
    if domain == '@gmail.com':
        return True
    return False
    
def validPassword(email,password):
    if len(password) == 16 and password.isalpha():
        try:
            yagmail.SMTP(email, password)
            return True
        except:
            logger.warn("Failed authentication with google for email %s",email)
    return False