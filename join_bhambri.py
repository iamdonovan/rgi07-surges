import os
import pandas as pd
import geopandas as gpd
import tools


# set the directory where the RGI folders are kept
rgi_dir = '/media/bob/seabox/RGI/'

data = pd.read_csv('xlsx_docx/BhambriSupplement.csv')
data = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['L2'], data['L1'], crs='epsg:4326'))

# I believe Bhambri is all observed surges, so they get a value of 3
data['SurgeType'] = 3

# only working with RGI14
namedict_v7 = tools.rgi7_namedict()
name_v7 = tools.format_v7('14', namedict_v7['14'])

v7_outlines = gpd.read_file(os.path.join(rgi_dir, 'v7b', name_v7, name_v7 + '.shp'))

v7_outlines['surge_type'] = 9
v7_outlines.surge_type = v7_outlines.surge_type.astype(int)

# set the index to the rgi_id
v7_outlines.set_index('rgi_id', inplace=True)

v7_outlines, missing = tools.join_attrs(v7_outlines, data, 'BhambriSupplement.csv')

v7_outlines[['surge_type']].to_csv(os.path.join('attributes', name_v7 + '_bhambri.csv'), index=True)
