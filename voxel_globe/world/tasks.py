from ..common_tasks import app
import voxel_globe.world.models

@app.task
def getArea(id):
  country = voxel_globe.world.models.WorldBorder.objects.get(id=id)
  return country.area;
