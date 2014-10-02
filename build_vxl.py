import os
from os import environ as env
from os.path import join as path_join
from disutils.dir_util import mkpath
import subprocess;

if __name__=='__main__':
  mkpath(env['VIP_VXL_DIR']);
  os.chdir(env['VIP_VXL_DIR']);
  
  cmake_options = [];
  
  tmp = env.pop('VIP_CMAKE_PLATFORM', None);
  if tmp:
    cmake_options += ['-G', tmp];

  tmp = env.pop('VIP_VXL_CMAKE_OPTIONS', None);
  if tmp:
    cmake_options += eval('[' + tmp + ']');
    #Sure, this may be generally unsafe, but only the user administrating the 
    #computer should be able to set and run this, so I choose to trust them

  pid = subprocess.Popen([env['VIP_CMAKE'], path_join(env['VIP_PROJECT_ROOT'], 'vxl_src')] + cmake_options);