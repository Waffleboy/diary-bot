# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 21:43:12 2016

@author: waffleboy
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dbWrapper as db
import psycopg2,os

engine = create_engine(os.environ["DIARYBOT_DB"],echo=True)

def generateSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def createTestUser(engine):
    currUser = db.User(username = "waffleboy", 
                        telegram_id = 113756492,
                        target_emails = {"emails":["ilovejingyin2@gmail.com"]},
                        email = "thiru1337@gmail.com",
                        app_password = "qokvoupsarpqcpyd")
    session = generateSession()
    session.add(currUser)
    session.commit()
    session.close()
    
    
conn = psycopg2.connect(os.environ["DIARYBOT_DB"])
cur = conn.cursor()
cur.execute("""SELECT * from users""")
rows = cur.fetchall()