from voxel_globe.common_tasks import app, VipTask
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
#VERY useful, use this logger for any logging
@app.task(base=VipTask, bind=True)
def runSomeTask(self, stuff, history=None):
  logger.debug('hi %s' % stuff);
  return (stuff, 'good')