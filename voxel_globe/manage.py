#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
  os.environ.setdefault("VIP_MANAGE_SERVER", "1")
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voxel_globe.vip.settings")

  from django.core.management import execute_from_command_line

  execute_from_command_line(sys.argv)
