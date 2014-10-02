#!/usr/bin/env python

from os import environ as env;
from os.path import join as path_join
import os
import tempfile
from subprocess import Popen
import time;

from pprint import pprint
from django.contrib.gis.utils.ogrinspect import mapping
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from django.core import management

logStdOut = None;
logStdErr = None;

def runCommand(cmd, haltOnFail=False, cwd=None):
  logStdOut.write('Running %s\n\n'%' '.join(cmd))
  #print ' '.join(cmd)
  returnCode = Popen(cmd, stdout=logStdOut, stderr=logStdErr, cwd=cwd).wait();
  if haltOnFail and returnCode:
    raise Exception('Run command failed [%d]: %s' % (returnCode, ' '.join(cmd)))
  return returnCode;

def pg_initdb():
  fid = tempfile.NamedTemporaryFile(mode='w', delete=False);
  fid.write(env['VIP_POSTGRESQL_PASSWORD']);
  fid.close();
  cmd = ['pg_ctl', 'initdb', 
         '-D', env['VIP_POSTGRESQL_DATABASE'],
         '-o', ' '.join(['--username', env['VIP_POSTGRESQL_USER'],
                         '--pwfile', fid.name,
                         '--auth', env['VIP_POSTGRESQL_AUTH'],
                         '--encoding', env['VIP_POSTGRESQL_ENCODING'],
                         '--locale', env['VIP_POSTGRESQL_LOCALE']])]
  runCommand(cmd, haltOnFail=False);
  os.remove(fid.name);

def pg_startdb():
  cmd=['pg_ctl', 'start', 
       '-D', env['VIP_POSTGRESQL_DATABASE'],
       '-o', env['VIP_POSTGRESQL_SERVER_CREDENTIALS']]
  runCommand(cmd, haltOnFail=True);

def pg_stopdb():
  cmd=['pg_ctl', 'stop', 
       '-D', env['VIP_POSTGRESQL_DATABASE'],
       '-m', 'fast',
       '-o', env['VIP_POSTGRESQL_CREDENTIALS']]
  runCommand(cmd, haltOnFail=False);

def pg_isready():
  cmd=['pg_isready', 
       '-d', 'postgres'] + env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
  return runCommand(cmd, haltOnFail=False);

def pg_createdb(databaseName, otherArgs=[]):
  cmd = ['createdb']
  cmd += env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
  cmd += ['-e', #Verbosity!
          '--encoding', env['VIP_POSTGRESQL_ENCODING']]
  cmd += otherArgs + [databaseName]
  runCommand(cmd, haltOnFail=False);
  
def pg_dropdb(databaseName):
    cmd = ['dropdb']
    cmd += env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
    cmd += ['-e', #Verbosity!
            databaseName]
    runCommand(cmd, haltOnFail=False);
    
def psql(databaseName, sqlCmd):
  cmd=['psql']
  cmd += env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
  cmd += ['-d', databaseName, '-c'] + [sqlCmd];
  return runCommand(cmd, haltOnFail=False);

def load_world_data():
  from world import models
  #Chicken egg problem. You can't import until after postgres has started
  
  world_shp = env['VIP_DJANGO_REGRESSION_SHAPEFILE']
  #print world_shp, '\n'

  ds = DataSource(world_shp)

  geometryName = u'mpoly';

  if 1: #Completely optional
    from django.contrib.gis.utils.ogrinspect import _ogrinspect
    print >>logStdOut, 'Your class model SHOULD look like this:\n'
    print >>logStdOut, '\n'.join([s for s in _ogrinspect(ds, 'WorldBorder', geom_name=geometryName, layer_key=0, srid=4326, multi_geom=True)]);

  world_mapping = mapping(ds, multi_geom=True, geom_name=geometryName, layer_key=0);

  print >>logStdOut, 'Loading database using mapping:'
  pprint(world_mapping, stream=logStdOut)

  try:
    lm = LayerMapping(models.WorldBorder, world_shp, world_mapping,
                      transform=False, encoding='iso-8859-1');
    lm.save(strict=True, verbose=True, stream=logStdOut);
  except:
    print 'Failed to load mapping data. It probably already exists!'
  
if __name__=='__main__':
  logStdOut = open(path_join(env['VIP_LOG_DIR'], 'db_setup_out.log'), 'w');
  logStdErr = open(path_join(env['VIP_LOG_DIR'], 'db_setup_err.log'), 'w');
  
  if pg_isready()==0:
    print "Error: Postgresql server is alreay running. Please stop it before\n", \
          "       running database setup"
    exit(1);

  if env['VIP_INITIALIZE_DATABASE_CONFIRM']=='1':
    print 'Would you like to delete the following databases\n' \
          '  %s\n' % env['VIP_POSTGRESQL_DATABASE_NAME'], \
          '(No means you will attempt to recreate on top of the existing DB)'
    deleteDatabase = raw_input('Delete database if exists [Y/n]?:');
  else:
    deleteDatabase = 'Y';
  
  if len(deleteDatabase) and deleteDatabase[0]=='Y':
    deleteDatabase = True;
  else:
    deleteDatabase = False;
    
  print '********** Initilizing database **********'
  pg_initdb();

#createuser -P
#psql GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;

  print '********** Starting database **********'
  pg_startdb();
  
  print '********** Waiting for database to come up **********'
  while 1:
    if pg_isready() == 0:
      print 'Database ready!'
      break;
    print 'Waiting for database to come up...'
    time.sleep(1);
  
  if deleteDatabase:
    print '********** Deleting database %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
    pg_dropdb(env['VIP_POSTGRESQL_DATABASE_NAME'])
  
  print '********** Creating postgis template **********'
  pg_createdb('template_postgis');
  psql('template_postgis', 'CREATE EXTENSION postgis;')
  psql('template_postgis', 'CREATE EXTENSION postgis_topology;')
  psql('template_postgis', 'CREATE EXTENSION fuzzystrmatch;')
  psql('template_postgis', 'CREATE EXTENSION postgis_tiger_geocoder;')

  # Enabling users to alter spatial tables. Do we want this?
  psql('template_postgis', "GRANT ALL ON geometry_columns TO PUBLIC;");
  psql('template_postgis', "GRANT ALL ON geography_columns TO PUBLIC;");
  psql('template_postgis', "GRANT ALL ON spatial_ref_sys TO PUBLIC;");

  #Make it a template
  psql('postgres', "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';");

  print '********** Creating database %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
  pg_createdb(env['VIP_POSTGRESQL_DATABASE_NAME'], otherArgs=['-T', 'template_postgis'])

  print '********** Creating django tables in %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
  management.call_command('syncdb', interactive=False, stdout=logStdOut)
  #syncdb will become migrate in django 1.7
  
  print '********** Creating Djanjo Superuser %s **********' % env['VIP_DJANGO_USER']
  from django.contrib.auth.models import User as DjangoUser; 
  #Chicken egg again
  with open(env['VIP_DJANGO_PASSWD'], 'rb') as fid:
    pw = fid.readline().strip()
    fid.close();
  try:
    user = DjangoUser.objects.create_superuser(env['VIP_DJANGO_USER'], env['VIP_EMAIL'], 'changeme');
  except:
    user = DjangoUser.objects.get(username=env['VIP_DJANGO_USER'])

  user.password = pw;
  user.save();

  print '********** Populating database WorldBorder **********'
  load_world_data();

  print '********** Checking for sample meta data **********'
  if not os.path.exists(path_join(env['VIP_PROJECT_ROOT'], 'images', '20100427161943-04003009-05-VIS')):
    import Tkinter
    import tkMessageBox
    top = Tkinter.Tk();
    top.withdraw();
    tkMessageBox.showinfo("Download needed", "Images missing. Please download:\n"+
                          "/pgm/finderdata2/projects/nga_p2/purdue_sample.zip\n"+
                          "And extract into %s" % env['VIP_PROJECT_ROOT'])
    exit(1);

  if False and not os.path.exists(path_join(env['VIP_DATABASE_DIR'], 'meta', '20100427161943-04003009-05-VIS')):
    '''Use this for when you have camera models in the database dir to add'''
    import Tkinter
    import tkMessageBox
    top = Tkinter.Tk();
    top.withdraw();
    tkMessageBox.showinfo("Download needed", "Images missing. Please download:\n"+
                          "/pgm/finderdata2/projects/nga_p2/purdue_sample.zip\n"+
                          "And extract into %s" % env['VIP_PROJECT_ROOT'])
    exit(1);

  print '********** Populating sample meta databases **********'
  
  import tasks;
  t = tasks.add_control_point.apply(args=(os.path.join(env['VIP_DATABASE_DIR'], 'NGASBIR.txt'),));
  if t.failed():
    print t.traceback;
    raise t.result;
  t = tasks.add_sample_images.apply((os.path.join(env['VIP_PROJECT_ROOT'], 'images'),))
  if t.failed():
    print t.traceback;
    raise t.result;

  
  t = tasks.add_sample_tie_point.apply(args=(os.path.join(env['VIP_DATABASE_DIR'], 'Purdue_Sample9_all_meta.xml'),
                                             os.path.join(env['VIP_DATABASE_DIR'], 'survey_pts_in_lvcs_selected.txt'),
                                             0,
                                             range(10)));
  if t.failed():
    print t.traceback;
    raise t.result;
  t = tasks.update_sample_tie_point.apply(args=(path_join(env['VIP_DATABASE_DIR'], 'latest_tiepoints.txt'),));
  if t.failed():
    print t.traceback;
    raise t.result;
 
  print '********** Stopping database **********'
  pg_stopdb();

  print '********** Waiting for database to go down **********'
  while 1:
    if pg_isready() != 0:
      print 'Database DOOOOOooooooown!'
      break;
    print 'Waiting for database to go down...'
    time.sleep(1);

#  print "Don't forget you probably need to run web/deploy.bat|bsh after starting the services"
