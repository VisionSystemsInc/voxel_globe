import os
os.environ.data.pop('', None);
#see wsgi.py why

from Cookie import SimpleCookie
import datetime
import pytz

from django.contrib.auth import SESSION_KEY
from django.conf import settings

#from django.contrib.auth.models import User
from django import db
from django.contrib.sessions.models import Session
from django import setup;
setup();

'''def check_password(environ, user, password):
    return True
    db.reset_queries() 
    
    check_password.a+=1
    print environ['HTTP_COOKIE'], check_password.a
    
    kwargs = {'username': user, 'is_active': True} 

    try: 
        try: 
            user = User.objects.get(**kwargs) 
        except User.DoesNotExist: 
            return None

        if user.check_password(password): 
            return True
        else: 
            return False
    finally: 
        db.connection.close()
check_password.a = 1'''

'''class SessionObject(object):
  def __init__(self, sessionId, expireTime):
    self.sessionId = sessionId;
    self.expireTime = expireTime;
    
  def __eq__(self, rhs):
    return self.sessionId == rhs.sessionId;'''

def allow_access(environ, host):
  #print '\n'.join(map(lambda x: '%s:  %s' % x, zip(environ.keys(), environ.values())))
  #print environ['REQUEST_URI'], environ['SCRIPT_NAME']
  try:
    cookie = SimpleCookie(environ['HTTP_COOKIE'])
  except KeyError:
    #No cookie == no permission
    return False;
  
  #Special overide for INTERAL services, NOT FOR WEB SERVICES!!!
  #There should be no way they have the secret key!
  try:
    secret = cookie['secretkey'].value
    #print 'is "%s" == "%s"?' % (secret, settings.SECRET_KEY) 
    if secret == settings.SECRET_KEY:
      return True;
  except KeyError:
    pass;
  
  try:
    sessionId = cookie[settings.SESSION_COOKIE_NAME].value;
  except KeyError:
    #No session id -> not logged in -> immediate access denied
    return False
  now = datetime.datetime.now(tz=pytz.utc);

  if now > allow_access.nextCheck:
    #if checkFrequency has passed, clear the list
    allow_access.validSessions = {}
    #print 'Cleared cache'
    allow_access.nextCheck = now + allow_access.checkFrequency;
  
  try: 
    #print 'Check in cache'
    #Check if in list
    expireTime = allow_access.validSessions[sessionId]
    #Get index
    #print 'In cache'
  except KeyError: #Session not in dictionary
    #print 'Not in cache', allow_access.validSessions
    try:
      #print 'check in session db', sessionId
      db.reset_queries()
      session = Session.objects.get(pk=sessionId)
      if not SESSION_KEY in session.get_decoded():
        #If session KEY is not in the data stream there this is not a logged in SESSION
        return False
    except Session.DoesNotExist:
      #Not in session DB
      #print 'Not in session db'
      return False;
    finally:
      db.connection.close()
  
    #if it's in the database
    allow_access.validSessions[sessionId] = session.expire_date;
    #Add to cache
    expireTime = session.expire_date;
    #print 'in session db'


  if expireTime > now:
    #Valid session by expire time
    #print 'Valid time'
    return True
  else:
    #print 'Invalid time'
    return False
  


  '''try:
    session = SessionObject(cookie['sessionid'].value, datetime.datetime.now(tz=pytz.utc));
    print 'Session found', session.sessionId
    
    #Handle clearing cache
    if session.expireTime > allow_access.nextCheck:
      #if checkFrequency has passed, clear the list
      allow_access.validSessions = []
      print 'Cleared cache'
    allow_access.nextCheck = session.expireTime + allow_access.checkFrequency;

    try:
      print 'Check in cache'
      #Check if in list
      validIndex = allow_access.validSessions.index(session)
      #Get index
      print 'In cache'
    except ValueError:#Session not in list
      print 'Not in cache'
      try:
        print 'check in session db', session.sessionId
        sessionDb = Session.objects.get(pk=session.sessionId)
        #if it's in the database
        allow_access.validSessions.append(sessionDb)
        validIndex = len(allow_access.validSessions)-1;
        #Add to cache
        print 'in session db'
      except Session.DoesNotExist:
        #Not in session DB
        print 'Not in session db'
        return False;

    if allow_access.validSessions[validIndex].expireTime > session.expireTime:
      #Valid session by expire time
      print 'Valid time'
      return True
    else:
      print 'Invalid time'
      return False
    
  except KeyError:
    #No session id -> not logged in -> immediate access denied
    return False'''
allow_access.validSessions = {}
allow_access.nextCheck = datetime.datetime.now(tz=pytz.utc);
allow_access.checkFrequency = datetime.timedelta(seconds=10); 