#I have to rename it, because apparently import subprocess will import MYSELF grrrr

''' This is a wrapper around Popen to help guarentee the calls in windows
    are indeed in the background. Use this instead of subprocess.Popen'''

import os
from subprocess import *

if os.name=='nt' and os.environ['VIP_DAEMON_BACKGROUND'] == '1':
  from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW 
  STARTUPINFO.dwFlags = STARTF_USESHOWWINDOW
