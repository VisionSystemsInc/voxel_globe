''' Master Celery Task file.
    
    Import all tasks you want the central celery daemon processing
    
    This CAN be used by other processes, but that it not the intent of this file
'''

#import celery app
from .common_task import app, VipTask

#Add additional tasks to the list here
import world_app.tasks
import tiepoint_app.tasks
import arducopter.tasks
import visualsfm.tasks