from celery import Celery

import scipy;
import numpy;

import world.models

app = Celery('tasks');
app.config_from_object('celeryconfig') #Don't need this because celeryd does it for me

@app.task
def add(x, y):
  a = numpy.random.random((x,x));
  aaa = a;
  for yy in xrange(y):
    aa = scipy.fft(aaa);
    aaa = scipy.ifft(aa);
  return numpy.abs(a-aaa).sum();

@app.task
def getArea(id):
  country = world.models.WorldBorder.objects.get(id=id)
  return country.area;
