# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 16:02:36 2016

@author: waffleboy
"""

import yagmail
import os
from datetime import date
import logging
import diarybot as db

logger = db.setupLogger()

# Main function
def processMessage(incomingMessage,action):
    logger.debug("Processing incoming message with action %s",action)
    successfulAction = False
    if action == "diaryLog":
        successfulAction = handleAction_DiaryLog(incomingMessage)
        
    # If more actions in the future
    return successfulAction
    
#==============================================================================
#                           Action Handlers
#==============================================================================

# Handle the "diaryLog" action
def handleAction_DiaryLog(incoming_message):
    successfulAction = False
    todaysDate = date.today()
    todaysDateStr = currentStrOfTimeFormat(todaysDate)
    successfulAction = sendEmail(todaysDateStr,incoming_message)
    return successfulAction
    
#==============================================================================
#                           Yagmail Functions
#==============================================================================
def sendEmail(todaysDate,incoming_message):
    logger.debug("Sending message: %s",incoming_message)
    incoming_message = removeCommand(incoming_message,"/log")
    yag = yagmail.SMTP(os.environ["MY_EMAIL_ADDRESS"], os.environ["MY_EMAIL_PASSWORD"])
    success = yag.send(os.environ["EMAIL_TO_SEND_TO"], todaysDate, incoming_message)
    success = True if success == {} else False
    if success:
        logger.info("Message successfully sent")
    else:
        logger.warn("Error with yagmail in sending message: %s",incoming_message)
    return success

#==============================================================================
#                              Misc Func
#==============================================================================
def currentStrOfTimeFormat(dateObject):
    return dateObject.strftime("%A, %d/%m/%Y")
    
def removeCommand(incoming_message,command):
    skipLength = len(command) + 1
    return incoming_message[skipLength:]