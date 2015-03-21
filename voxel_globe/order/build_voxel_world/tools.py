from boxm2_adaptor import create_scene_and_blocks
from vpgl_adaptor import create_lvcs, convert_local_to_global_coordinates

def create_scene(origin, lla1, lla2, scene_size, scene_dir, vox_size=1, block_len_xy = 100, block_len_z = 60):
  ''' Inputs
      origin, lla1, lla2 - 3 array - longitude, latitude, and altitude in degrees and meters
      scene_size - 3 array, x(east/west), y(north/south) and z(height) in meters
      vox_size in meters
      scene_dir - directory to write scene.xml in,
      block_xy - in meters
      block_z - in meters'''

  app_model = "boxm2_mog3_grey";
  #app_model = "boxm2_gauss_rgb";
  obs_model = "boxm2_num_obs";
  #obs_model = "boxm2_num_obs_single";
  
  ## NGA SBIR P2 - AngelFirePurdue dataset scene
  
  #scene_dir = "D:/projects/NGA_P2/AngelFirePurdueSBIR/model_geo";
  #scene_dir = "C:/projects/NGA_P2/AngelFirePurdueSBIR/model_sfm_transformed";
#  vox_size = 0.25;   # in meters

  #lvcs = create_lvcs(lla[1], lla[0], lla[2], "wgs84");
  #(lat1, lon1, elev1) = convert_local_to_global_coordinates(-lvcs,scene_size[0]/2.0,-scene_size[1]/2.0,-scene_size[2]/2.0)
  #(lat2, lon2, elev2) = convert_local_to_global_coordinates(lvcs,scene_size[0]/2.0,scene_size[1]/2.0,scene_size[2]/2.0)
  #lon = -86.914938; lat = 40.4222334; elev = 140; # lower corner
  #lon2 = -86.909095; lat2 = 40.425837; elev2 = 200; # upper corner
  #origin_lon = lla[0]; 
  #origin_lat = lla[1]; 
  #origin_elev = lla[2];
  #block_len_xy = 100;  # in meters, larger blocks require more memory on GPU, the larger the better but set according to available memory
  #block_len_z = 60;  # in meters, set with similar constraints to xy
  
  xml_name_prefix = "scene";
  create_scene_and_blocks(scene_dir, app_model, obs_model, origin[0], origin[1], origin[2], lla1[0], lla1[1], lla[2], lla[0], lla[1], lla[2], vox_size, block_len_xy, block_len_z, "utm", 1, xml_name_prefix);


