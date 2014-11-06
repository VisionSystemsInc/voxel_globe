from vip.common_task import app
import world.models

@app.task
def getArea(id):
  country = world.models.WorldBorder.objects.get(id=id)
  return country.area;
