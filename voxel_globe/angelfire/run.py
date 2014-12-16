import django
from .tasks import add_control_point, add_sample_images, add_sample_tie_point, update_sample_tie_point
import os
from os import environ as env
from os.path import join as path_join

if __name__ == '__main__':
  django.setup();
  
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

  print '********** Populating sample meta databases **********'

  t = add_control_point.apply(args=(os.path.join(env['VIP_PROJECT_ROOT'], 'images', 'NGASBIR.txt'),));
  if t.failed():
    print t.traceback;
    raise t.result;
  t = add_sample_images.apply((os.path.join(env['VIP_PROJECT_ROOT'], 'images'),))
  if t.failed():
    print t.traceback;
    raise t.result;

  
  t = add_sample_tie_point.apply(args=(os.path.join(env['VIP_PROJECT_ROOT'], 'images', 'Purdue_Sample9_all_meta.xml'),
                                             os.path.join(env['VIP_PROJECT_ROOT'], 'images', 'survey_pts_in_lvcs_selected.txt'),
                                             0,
                                             range(10)));
  if t.failed():
    print t.traceback;
    raise t.result;
  t = update_sample_tie_point.apply(args=(path_join(env['VIP_PROJECT_ROOT'], 'images', 'latest_tiepoints.txt'),));
  if t.failed():
    print t.traceback;
    raise t.result;