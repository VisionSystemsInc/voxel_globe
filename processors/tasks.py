from celery import Celery, Task, group

import scipy;
import numpy;

import world.models
import meta.models

from os import environ as env;

app = Celery('tasks');
app.config_from_object('celeryconfig') #Don't need this because celeryd does it for me

import json;

@app.task(bind=True)
def add(self, x, y):
  a = numpy.random.random((x,x));
  aaa = a;
  for yy in xrange(y):
    aa = scipy.fft(aaa);
    aaa = scipy.ifft(aa);

  return [numpy.abs(a-aaa).sum(), self.request.id]

@app.task
def getArea(id):
  country = world.models.WorldBorder.objects.get(id=id)
  return country.area;

class VipTask(Task):
  abstract = True
  
  def __createServiceIntanceEntry(self, taskID=None, inputs=None):
    '''Create initial database entry for service instance, and return the taskID'''

    serviceInstance = meta.models.ServiceInstance(
                          inputs=json.dumps(inputs),
                          status="Creating",
                          user="NAY",
                          serviceName="NAY", #Next TODO
                          outputs='NAY', taskID='NAY');
    serviceInstance.save();
    if taskID is None:
      taskID = serviceInstance.id;
    serviceInstance.taskID = taskID;
    serviceInstance.save()
    return taskID;
    
  def __updateServiceIntanceEntry(self, output, task_id, status, args=None, kwargs=None):
###    try:
###      serviceInstance = meta.models.ServiceInstance.objects.get(id=task_id);
###    except (ValueError, meta.models.ServiceInstance.DoesNotExist):
###      #Perhaps the task id is missing or is not the primary key
    try:
###      #Maybe it's the task id, in the case of uuid4
      serviceInstance = meta.models.ServiceInstance.objects.get(taskID=task_id);
    except meta.models.ServiceInstance.DoesNotExist:
      #Else it's just missing, create it
      status="Impromptu:"+status;
      self.__createServiceIntanceEntry(task_id, (args, kwargs));
      serviceInstance = meta.models.ServiceInstance.objects.get(taskID=task_id);

    serviceInstance.outputs = json.dumps(output)
    serviceInstance.taskID = task_id;
    serviceInstance.status = status;
    serviceInstance.save();

  def apply_async(self, args=None, kwargs=None, task_id=None, *args2, **kwargs2):
    task_id = self.__createServiceIntanceEntry(task_id, (args, kwargs));
    
    return super(VipTask, self).apply_async(args=args, kwargs=kwargs, task_id=task_id, *args2, **kwargs2)
  
  def apply(self, args=None, kwargs=None, task_id=None, *args2, **kwargs2):
    ''' Automatically create task_id's based off of new primary keys in the database''' 
    task_id = self.__createServiceIntanceEntry(task_id, (args, kwargs));
    
    return super(VipTask, self).apply(args=args, kwargs=kwargs, task_id=task_id, *args2, **kwargs2)
  
#  def after_return(self, status, retval, task_id, args, kwargs, einfo): #, *args2, **kwargs2
  def on_success(self, retval, task_id, args, kwargs):
    #I can't currently tell if apply or apply_asyn is called, but I don't think I care
    self.__updateServiceIntanceEntry(retval, task_id, 'Success', args, kwargs);
  
  def on_failure(self, exc, task_id, args, kwargs, einfo):
    self.__updateServiceIntanceEntry(str(einfo), task_id, 'Failure', args, kwargs);

@app.task(base=VipTask)
def test(abc=None, *args, **kwargs):
  if abc==15:
    raise Exception("ouch");
  return 42

@app.task(base=VipTask)
def add_sample_data():
  print 'Adding Sample data'
  img = meta.models.Image(name="Oxford Codrington Library", imageWidth=999, imageHeight=749, 
                          numberColorBands=3, pixelFormat='b', fileFormat='zoom', 
                          imageURL='http://%s:%d/static/meta/images/camelot-UK_2012OxfordUniversity-42' % 
                                   (env['NPR_POSTGRESQL_HOST'], int(env['NPR_HTTPD_PORT'])));
                                  #I know postgresql here is WRONG, don't care right now, it WILL be image server!
  img.save();

  tp = meta.models.ImageTiePoint(x=100, y=100, name='Some point', image = img);
  tp.save();
  
  gtp = meta.models.GeoTiePoint(name='Some geo point', 
           description='None provided. Just some point trying to make a point in life',
           latitude=51.7534, longitude=-1.2539, altitude=89.2,
           apparentLatitude=51.753416, apparentLongitude=-1.254033, apparentAltitude=71)
  gtp.save();
  
  tp = meta.models.ImageTiePoint.objects.get(name='Some point');
  #This previous command is NOT neccesary, since tp is still in memory, 
  #HOWEVER I wanted to provice an update example
  tp.geoPoint = gtp;
  tp.save();

#TODO
#Define Add task
#--Addes a task, retrieve data from database, etc...
#--Gets a GUID and sets task ID
#--Adds entry for service/taskID into ____ table

#Workflows?
#Need to read up on Celery to see if it already does workflows

'''
Avoid launching synchronous subtasks

Having a task wait for the result of another task is really inefficient, and may even cause a deadlock if the worker pool is exhausted.

Make your design asynchronous instead, for example by using callbacks.

Bad:

@app.task
def update_page_info(url):
    page = fetch_page.delay(url).get()
    info = parse_page.delay(url, page).get()
    store_page_info.delay(url, info)

@app.task
def fetch_page(url):
    return myhttplib.get(url)

@app.task
def parse_page(url, page):
    return myparser.parse_document(page)

@app.task
def store_page_info(url, info):
    return PageInfo.objects.create(url, info)

Good:

def update_page_info(url):
    # fetch_page -> parse_page -> store_page
    chain = fetch_page.s() | parse_page.s() | store_page_info.s(url)
    chain()

@app.task()
def fetch_page(url):
    return myhttplib.get(url)

@app.task()
def parse_page(page):
    return myparser.parse_document(page)

@app.task(ignore_result=True)
def store_page_info(info, url):
    PageInfo.objects.create(url=url, info=info)

Here I instead created a chain of tasks by linking together different subtask()'s. You can read about chains and other powerful constructs at Canvas: Designing Workflows.'''