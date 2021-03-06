from channels import Group
from channels.sessions import enforce_ordering
import json
from voxel_globe.websockets.models import LogMessage
from voxel_globe.meta.models import ServiceInstance
from voxel_globe.task.views import pretty_name
from voxel_globe.websockets import consumers

from celery.utils.log import get_task_logger
import logging
logger = get_task_logger(__name__)
logging.addLevelName(logging.FATAL, 'FATAL')

# TODO: turn these 3 on/off from an environment variable according to level of 
# verbosity the user wants
def debug(task, message_text):
  # send_log(task.request.id, task.name, message_text, 'Debug')
  pass

def info(task, message_text):
  # send_log(task.request.id, task.name, message_text, 'Info')
  pass

def warn(task, message_text):
  # send_log(task.request.id, task.name, message_text, 'Warn')
  pass

def error(task, message_text):
  send_log(task.request.id, task.name, message_text, 'Error')

def fatal(task, message_text):
  send_log(task.request.id, task.name, message_text, 'Fatal')

def message(task, message_text):
  send_log(task.request.id, task.name, message_text, 'Message')

# @enforce_ordering(slight=True)
def send_log(task_id, task_name, message_text, log_level):
  if log_level == 'Message':
    log_type = 'message'
    logger.info("Message[{}({})]: {}".format(task_name, task_id, message_text))
  else:
    log_type = 'log'
    logger.log(logging.getLevelName(log_level.upper()), 
               "[{}({})]: {}".format(task_name, task_id, message_text))

  service_instance = ServiceInstance.objects.get(id=int(task_id))
  user = service_instance.user

  if not user:
    logger.warning("No user for task {} ({}) ".format(task_name, task_id))
    return

  msg = LogMessage.objects.create(
    message_text=message_text,
    message_type=log_level[0].lower(),
    task_id=task_id,
    owner=user
  )

  task = {
    "id" : task_id,
    "name" : pretty_name(task_name)
  }

  to_json = {
    "task" : task,
    "type" : log_type,
    "log_level" : log_level,
    "message_text" : message_text,
    "log_id" : msg.pk
  }

  message = {
    "text" : json.dumps(to_json),
  }

  Group("ws_logger_%s" % user.id).send(message)

# @enforce_ordering(slight=True)
def send_status_update(task_id, task_name, status, result):
  service_instance = ServiceInstance.objects.get(id=int(task_id))
  user = service_instance.user

  if not user:
    logger.warning("No user for task {} ({}) ".format(task_name, task_id))
    return

  task = {
    "id" : task_id,
    "path" : task_name,
    "name" : pretty_name(task_name),
    "state" : status,
    "result" : result
  }

  to_json = {
    "task" : task,
    "type" : "status_update"
  }

  message = {
    "text" : json.dumps(to_json)
  }

  Group("ws_logger_%s" % user.id).send(message)