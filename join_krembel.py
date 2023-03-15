import os
import pandas as pd
import geopandas as gpd
import tools


data = pd.read_excel('xlsx_docx/RuthKrembel_Inventory.xlsx', sheet_name='New surging glaciers', header=1)
del data['Unnamed: 0'] # remove empty first column

data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce') / 1e9
data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce') / 1e9

# the only surges in the table with no geographic information are outlets of GrIS, or covered by Bhambri w/ coords
data.dropna(subset=['Longitude', 'Latitude'], how='any', inplace=True)

data = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['Longitude'], data['Latitude'], crs='epsg:4326'))

# now, attach a surge attribute to each row
data.loc[data['Surge Duration [y]'] != 'no data', 'SurgeType'] = 3
data.loc[data['Surge Duration [y]'] == 'no data', 'SurgeType'] = 1

# make the output folder if it doesn't exist
os.makedirs('attributes', exist_ok=True)

# set the directory where the RGI folders are kept
rgi_dir = '/media/bob/seabox/RGI/'

# get the RGI v7 namedict
namedict_v7 = tools.rgi7_namedict()

# load the O1 outlines
o1_outlines = gpd.read_file(os.path.join(rgi_dir, 'v6.0', '00_rgi60_regions/00_rgi60_O1Regions.shp'))

# drop the two bits that straddle the stupid dateline
o1_outlines.drop([1, 10], inplace=True)

missing_pts = []

# now, loop through the different regions
for ind, row in o1_outlines.iterrows():
    outline = row['geometry']
    rgn = '{:02d}'.format(row['RGI_CODE'])

    # format the v7 name of the region
    name_v7 = tools.format_v7(rgn, namedict_v7[rgn])
    print(name_v7)

    # load the v7 outlines
    v7_outlines = gpd.read_file(os.path.join(rgi_dir, 'v7b', name_v7, name_v7 + '.shp'))
    # add a column for the ST_Nov, ST_Geo, and flagged
    v7_outlines['surge_type'] = 9
    v7_outlines.surge_type = v7_outlines.surge_type.astype(int)

    # set the index to the rgi_id
    v7_outlines.set_index('rgi_id', inplace=True)

    # get the points from the inventory that are in this region
    data_in = outline.contains(data.geometry)

    # set up the loop over the datasets
    dataname = 'RuthKremble_Inventory.xlsx'

    v7_outlines, missing = tools.join_attrs(v7_outlines, data.loc[data_in], dataname)

    missing_pts.append(missing)

    v7_outlines[['surge_type']].to_csv(os.path.join('attributes', name_v7 + '_krembel.csv'), index=True)
