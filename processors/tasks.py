''' Master Celery Task file.
    
    Import all tasks you want the central celery daemon processing
'''

#import celery app
from common_task import app, VipTask

#Add additional tasks to the list here
import world_tasks
import tiepoint_tasks