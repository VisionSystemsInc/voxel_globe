from django.contrib.auth.hashers import make_password
from os import environ as env
from getpass import getpass;

def get_pass():
  pw1=getpass("Please enter the password you would like to use for Django:")
  pw2=getpass("Please verify:")
  
  if pw1==pw2:
    return pw1;
  print 'Passwords do not much, please try again\n'
  
if __name__=='__main__':
  pw=None;
  while pw == None:
    pw=get_pass()

  with open(env['NPR_DJANGO_PASSWD'], 'wb') as fid:
    fid.write(make_password(pw));
  
  print '\nIs is done, best not forget the password now...';