import os
from os import environ as env
from os.path import join as path_join
from distutils.dir_util import mkpath
import subprocess;

from ast import literal_eval

if __name__=='__main__':
  vxlDir = path_join(env['VIP_VXL_DIR'], env['VIP_VXL_BUILD_TYPE'])
  mkpath(vxlDir);
  os.chdir(vxlDir);
  
  cmake_options = [];
  
  cmake_options += ['-G', env['VIP_CMAKE_PLATFORM']];
  cmake_options += ['-D', 'CMAKE_BUILD_TYPE='+env['VIP_VXL_BUILD_TYPE']];

  if env['VIP_CMAKE_PLATFORM']=="Eclipse CDT4 - Unix Makefiles":
    cmake_options += ['-D', 'CMAKE_ECLIPSE_GENERATE_SOURCE_PROJECT=True'];

  cmake_options += ['-D', 'CMAKE_INSTALL_PREFIX='+
                 path_join(vxlDir, 'install')];

  cmake_options += ['-D', 'EXECUTABLE_OUTPUT_PATH='+
                 path_join(vxlDir, 'bin')];

  cmake_options += ['-D', 'OPENCL_INCLUDE_PATH='+env['VIP_OPENCL_INCLUDE_PATH'],
                    '-D', 'OPENCL_LIBRARY_PATH='+env['VIP_OPENCL_LIBRARY_PATH']];

#  cmake_options += ['-D', 'OPENCL_LIBRARIES='+env['VIP_OPENCL_LIBRARY']]

  tmp = env.pop('VIP_CMAKE_ECLIPSE', None);
  if tmp:
    cmake_options += ['-D', 'CMAKE_ECLIPSE_EXECUTABLE='+tmp];

  # Pretty open options section. User can in theory, override anything here  

  tmp = env.pop('VIP_VXL_CMAKE_OPTIONS', None);
  if tmp:
    cmake_options += literal_eval('[' + tmp + ']');
    #Sure, this may be generally unsafe, but only the user administrating the 
    #computer should be able to set and run this, so I choose to trust them
    #Update. literal_eval should be "safe"...er

  tmp = env.pop('VIP_VXL_CMAKE_ENTRIES', None);
  if tmp:
    tmp = literal_eval('[' + tmp + ']');
    for entry in tmp:
      cmake_options += ['-D', entry];


  pid = subprocess.Popen([env['VIP_CMAKE']] + cmake_options + [path_join(env['VIP_PROJECT_ROOT'], 'vxl_src')]);
  pid.wait();

  pid = subprocess.Popen(['make', '-j', '8'], cwd=vxlDir);
  pid.wait();
