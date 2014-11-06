''' Master Celery Task file.
    
    Import all tasks you want the central celery daemon processing
    
    This CAN be used by other processes, but that it not the intent of this file
'''

#import celery app
from .common_task import app, VipTask

#Add additional tasks to the list here
import voxel_globe.world.tasks
import voxel_globe.tiepoint.tasks
import voxel_globe.arducopter.tasks
import voxel_globe.visualsfm.tasks