# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 21:48:02 2016

@author: waffleboy
"""

import os,datetime
import logger_settings
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String,DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logger_settings.setupLogger().getLogger(__name__)
Base = declarative_base()
engine = create_engine(os.environ["DIARYBOT_DB"])

""" DB Models """
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String,index=True)
    telegram_id = Column(Integer,index=True)
    email = Column(String,index=True)
    target_emails = Column(JSONB,default={"emails":[]})
    app_password = Column(String)
    times_used = Column(Integer,default = 0)
    last_used = Column(DateTime)
    properties = Column(JSONB,default = {})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return "<User(name='%s', telegram_id='%s' target_emails='%s', email='%s' , times_used = '%s', last_used = '%s')>" % (
                         self.username, self.telegram_id, self.target_emails, 
                         self.email, self.times_used, self.last_used)
                         
    def getTargetEmails(self):
        return self.target_emails["emails"]
    
    def getMyEmail(self):
        return self.email
    
    def getMyAppPassword(self):
        return self.app_password
    
#Base.metadata.drop_all(engine)                         
#Base.metadata.create_all(engine)

#==============================================================================
#                           Wrapper Functions
#==============================================================================

def signUpUser(user_data,update):
    telegram_id = user_data["telegram_id"]
    username = user_data["username"]
    target_emails = user_data["target_email"] #is a list
    email = user_data["my_email"]
    app_password = user_data["app_key"]
    logger.info("Creating user %s",str(user_data))
    try:
        currUser = User(username = username, 
                        telegram_id = telegram_id,
                        target_emails = {"emails":target_emails},
                        email = email,
                        app_password = app_password)
   
        session = generateSession()
        session.add(currUser)
        commitAndCloseSession(session)
        logger.info("User successfully created: id %s and username %s",telegram_id,username)
    except Exception as e:
        #update.message.reply_text("Failed to save your information! Contact @Waffleboy for help")
        logger.critical("Fail to save users information into database! Error log: %s",e)
        return False
    return True
    
def getUserFromTelegramID(telegram_id):
     session = generateSession(expire_on_commit = False)
     try:
         user = session.query(User).filter(User.telegram_id == telegram_id).first()
     except:
         logger.info("No such user exists in DB for id %s",telegram_id)
         user = None
     session.close()
     return user

def setLastUsed(user):
    try:
        logger.info("Setting last used for %s",user.username)
        user.last_used = datetime.datetime.now()
        session = generateSession()
        session.add(user)
        commitAndCloseSession(session)
        return True
    except:
        logger.warn("Fail to set last used for user %s",str(user))
    return False
    
def addToTimesUsed(user):
    try:
        logger.info("Increasing times used for %s",user.username)
        user.times_used += 1
        session = generateSession()
        session.add(user)
        commitAndCloseSession(session)
        return True
    except:
        logger.warn("Fail to increase times used for user %s",str(user))
    return False

def deleteUser(user):
    try:
        logger.info("Deleting User %s",str(user))
        session = generateSession()
        session.delete(user)
        commitAndCloseSession(session)
        return True
    except Exception as e:
        logger.warn("Error in deleting user %s",str(user))
        logger.exception(e)
    return False
        
def checkIfAlreadyRegistered(telegram_id):
    user = getUserFromTelegramID(telegram_id)
    if user:
        return True
    return False
#==============================================================================
#                            Misc Helpers
#==============================================================================

def generateSession(expire_on_commit = True):
    Session = sessionmaker(bind=engine)
    session = Session()
    if expire_on_commit == False:
        session.expire_on_commit = False
    return session

def commitAndCloseSession(session):
    session.commit()
    session.close()