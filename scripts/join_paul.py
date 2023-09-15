import os
import geopandas as gpd
import tools


# make the output folder if it doesn't exist
os.makedirs('attributes', exist_ok=True)

# set the directory where the RGI folders are kept
rgi_dir = '/media/bob/seabox/RGI/'

# get a list of region numbers, formatted as 2-digit strings
regions = ['{:02d}'.format(n) for n in range(1, 20)]

# the list of region names used in RGI v7
names_v7 = ['alaska', 'western_canada_usa', 'arctic_canada_north', 'arctic_canada_south', 'greenland_periphery',
            'iceland', 'svalbard_jan_mayen', 'scandinavia', 'russian_arctic', 'asia_north',
            'central_europe', 'caucasus_middle_east', 'asia_central', 'asia_south_west', 'asia_south_east',
            'low_latitudes', 'southern_andes', 'new_zealand', 'subantarctic_antarctic_islands']
# a dict of region numbers and names for RGI v7
namedict_v7 = dict(zip(regions, names_v7))

# load the O1 outlines
o1_outlines = gpd.read_file(os.path.join(rgi_dir, 'v6.0', '00_rgi60_regions/00_rgi60_O1Regions.shp'))

# drop the two bits that straddle the stupid dateline
o1_outlines.drop([1, 10], inplace=True)

# load the dataset from frank
points = gpd.read_file('joined_surges/joined_surges_fp.shp')
points['SurgeType'] = points['surge_type']

# now, loop through the different regions
for ind, row in o1_outlines.iterrows():
    outline = row['geometry']
    rgn = '{:02d}'.format(row['RGI_CODE'])

    # get ready to output any points that weren't matched automatically
    missing_pts = []

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

    # get the points from GeodatabaseSTglaciers.csv that are in this region
    paul_in = outline.contains(points.geometry)

    v7_outlines, missing = tools.join_attrs(v7_outlines, points.loc[paul_in], 'joined_surges_fp')

    v7_outlines[['surge_type']].to_csv(os.path.join('attributes', name_v7 + '_paul.csv'), index=True)
