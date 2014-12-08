import os
os.environ.data.pop('', None);
#see wsgi.py why

from django.contrib.auth.models import User
from django import db

from django import setup;

setup();

def check_password(environ, user, password):
    db.reset_queries() 
    
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
