from tasks import add_arducopter_images, add_sample_tie_point
import os
import django;

if __name__ == '__main__':
  django.setup();
   
  print '********** Populating arducopter images **********'
  t = add_arducopter_images.apply();
  if t.failed():
    raise t.result

  print '********** Populating arducopter tiepoints **********'
  t = add_sample_tie_point.apply(args=(os.path.join(os.environ['VIP_PROJECT_ROOT'], 'images', 'arducopter_tie_points.xml'),
                                       os.path.join(os.environ['VIP_PROJECT_ROOT'], 'images', 'arducopter_control_points.txt'),
                                       None,
                                       range(519)));
  if t.failed():
    raise t.result
