import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from glob import glob


def format_v7(rgn, name):
    """
    Given a region and a name, construct the RGI v7 region name for a file/folder

    :param str rgn: the region number (e.g., '01')
    :param str name: the region name (e.g., 'alaska')
    :return:
    """
    return '-'.join(['RGI2000', 'v7.0', 'G', '_'.join([rgn, name.lower()])])


def format_v6(rgn, name):
    """
    Given a region and a name, construct the RGI v7 region name for a file/folder

    :param str rgn: the region number (e.g., '01')
    :param str name: the region name (e.g., 'Alaska')
    :return:
    """
    return '_'.join([rgn, 'rgi60', name])


def load_csv(fn_csv, lon_col, lat_col):
    """
    Load a CSV and turn it into a GeoDataFrame

    :param str fn_csv: the filename of the CSV
    :param str lon_col: the column of the CSV corresponding to longitude
    :param str lat_col: the column of the CSV corresponding to latitude
    :return:
    """
    df = pd.read_csv(fn_csv)
    df.dropna(how='all', inplace=True)

    # add a geometry column to make it a geodataframe
    df['geometry'] = list(zip(df[lon_col], df[lat_col]))
    df['geometry'] = df['geometry'].apply(Point)

    gdf = gpd.GeoDataFrame(df)
    return gdf.set_crs(epsg=4326)


def join_attrs(outlines, points, data_name):
    """
    Use a spatial join to join points to outlines, then add the value of the "Surging" column from the points based
    on the

    :param GeoDataFrame outlines: The outlines to add an attribute to
    :param GeoDataFrame points: The points to use to add attributes
    :param str data_name: the name of the dataset, for keeping track of where missing glaciers come from.
    :returns:
        - outlines
        - missing
    """
    # join the points and the outlines using sjoin
    joined = points.sjoin(outlines)

    print('{} points not matched'.format(points.shape[0] - joined.shape[0]))
    # figure out which rows (if any) aren't matched
    if joined.shape[0] != points.shape[0]:
        missing = pd.DataFrame()
        missing['geometry'] = points.loc[~points.index.isin(joined.index), 'geometry']
        missing['dataset'] = data_name

    else:
        missing = None

    # first, drop duplicates from "index_right" in joined
    # since we don't care if multiple points end up in the same outline
    joined.drop_duplicates(subset=['index_right'], inplace=True)

    # now, get the rows that matched
    is_matched = outlines.index.isin(joined['index_right'])
    # set the RGI v6 surge flag to equal what we get out of the joined table
    outlines.loc[is_matched, 'SurgeType'] = outlines.join(joined.set_index('index_right'), lsuffix='_')['SurgeType']

    return outlines, missing


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

# load GeodatabaseSTglaciers.csv
geodatabase = load_csv('data/GeodatabaseSTglaciers.csv', 'CENLON', 'CENLAT')
geodatabase['Surging'] = 1

# load ST_November.csv
november = load_csv('data/ST_November.csv', 'CentLON', 'CentLAT')
november['Surging'] = 1

# now, loop through the different regions
for ind, row in o1_outlines.iterrows():
    outline = row['geometry']
    rgn = '{:02d}'.format(row['RGI_CODE'])

    # get ready to output any points that weren't matched automatically
    missing_pts = []

    # format the v7 name of the region
    name_v7 = format_v7(rgn, namedict_v7[rgn])
    print(name_v7)

    # load the v7 outlines
    v7_outlines = gpd.read_file(os.path.join(rgi_dir, 'v7b', name_v7, name_v7 + '.shp'))
    # add a column for the ST_Nov, ST_Geo, and flagged
    v7_outlines['surge_type'] = 9
    v7_outlines.surge_type = v7_outlines.surge_type.astype(int)

    # set the index to the rgi_id
    v7_outlines.set_index('rgi_id', inplace=True)

    # get the points from GeodatabaseSTglaciers.csv that are in this region
    geo_in = outline.contains(geodatabase.geometry)

    # get the points from ST_November.csv that are in this region
    nov_in = outline.contains(november.geometry)

    # set up the loop over the datasets
    datanames = ['GeodatabaseSTglaciers.csv', 'ST_November.csv']
    datasets = [geodatabase.loc[geo_in], november.loc[nov_in]]

    for name, points in zip(datanames, datasets):
        v7_outlines, missing = join_attrs(v7_outlines, points, name)
        missing_pts.append(missing)

    v7_outlines[['surge_type']].to_csv(os.path.join('attributes', name_v7 + 'sevestre.csv'), index=True)
