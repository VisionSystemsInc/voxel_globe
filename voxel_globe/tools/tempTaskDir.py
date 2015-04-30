
import os
from os import environ as env

from tempfile import mkdtemp

class AutoCleanDir(str):
  def __new__(cls, obj, *args, **kwargs):
    ''' Silly immutable types '''
    return super(AutoCleanDir, cls).__new__(cls, obj)

  def __init__(self, obj, cleanup=True):
    ''' str constructor, with an extra cleanup argument
        if cleanup is True, when this variable is destroyed, so
        '''
    self.cleanup = cleanup
    super(AutoCleanDir, self).__init__(obj)

#Consider PERMISSIONS for directories that STAY, it's ALWAYS 700, you'll need to change it
def getTaskDir(cleanup=True):
  ''' Creates and returns a new processing directory for a celery task '''
  if not os.path.exists(env['VIP_TEMP_DIR']):
    from distutils.dir_util import mkpath
    mkpath(env['VIP_TEMP_DIR']);
  #make instance specific directory
  if env['VIP_CONSTANT_TEMP_DIR'] == '1':
    processingDir = env['VIP_TEMP_DIR'];
  else:
    processingDir = mkdtemp(dir=env['VIP_TEMP_DIR']);

  return AutoCleanDir(processingDir, cleanup=cleanup)

