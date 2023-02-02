#FROM create_dem.py
import os
from doris.prepare_stack.create_dem import CreateDem
import geopandas as gpd
#from shapely.geometry import Polygon

dem_out_folder = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_32_WaddenSea/dem_download'
dem_calc_folder = '/media/anurag/AK_WD/Sentinel_Processing/Doris_Processing_20_enschede/intermediate_dem'
aoi_file = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_32_WaddenSea/AOI/aoi_wadden.shp'

dem_out = os.path.join(dem_out_folder, 'dem.raw')
dem_var = os.path.join(dem_out_folder, 'dem.raw.var')

srtm_username = 'annie123'
srtm_password = 'Annie123'

bbox = gpd.read_file(aoi_file).values[0][1].bounds

lats = [bbox[1], bbox[3]]
lons = [bbox[0], bbox[2]]

#lats = [-12.95, -12.85]
#lons = [-38.5, -38.4]


dem = CreateDem()

dem.create(out_file = dem_out, var_file = dem_var, resample=None,
        doris_input=True, lats=lats, lons=lons, rounding=1, border=.5,
            data_folder=dem_calc_folder, quality='SRTM1',
            password=srtm_password, username=srtm_username)
