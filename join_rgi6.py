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


# create two new directories
os.makedirs('outlines', exist_ok=True)

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

# the list of region names used in RGI v7
names_v6 = ['Alaska', 'WesternCanadaUS', 'ArcticCanadaNorth', 'ArcticCanadaSouth', 'GreenlandPeriphery',
            'Iceland', 'Svalbard', 'Scandinavia', 'RussianArctic', 'NorthAsia', 'CentralEurope',
            'CaucasusMiddleEast', 'CentralAsia', 'SouthAsiaWest', 'SouthAsiaEast', 'LowLatitudes',
            'SouthernAndes', 'NewZealand', 'AntarcticSubantarctic']
# a dict of region numbers and names for RGI v6
namedict_v6 = dict(zip(regions, names_v6))

# now, loop through the different regions
for rgn in regions:
    # format the v7 name of the region
    name_v7 = format_v7(rgn, namedict_v7[rgn])
    print(name_v7)

    # format the v6 name of the region
    name_v6 = format_v6(rgn, namedict_v6[rgn])

    # load the v7 outlines
    v7_outlines = gpd.read_file(os.path.join(rgi_dir, 'v7b', name_v7, name_v7 + '.shp'))
    v7_outlines['SurgeType'] = 9  # set to 9 by default
    v7_outlines['SurgeType'] = v7_outlines['SurgeType'].astype(int)

    # set the index to the rgi_id
    v7_outlines.set_index('rgi_id', inplace=True)

    # load the v6 outlines
    v6_outlines = gpd.read_file(os.path.join(rgi_dir, 'v6.0', name_v6, name_v6 + '.shp'))

    # now, subset RGI v6
    is_surgetype = (v6_outlines.Surging == 1) | (v6_outlines.Surging == 2) | (v6_outlines.Surging == 3)
    surge_outlines = v6_outlines.loc[is_surgetype]
    surge_outlines.set_index('RGIId', inplace=True)

    overlap = v7_outlines.sjoin(surge_outlines)

    # should probably convert to a projected CRS for this...
    for ind, row in surge_outlines.iterrows():
        # get all of the outlines that overlap with this one
        overlapping = overlap.loc[overlap['RGIId'] == ind]

        # get the fraction of this outline's area that each overlap equals
        overlaps = np.array([row['geometry'].intersection(o['geometry']).area for _, o in overlapping.iterrows()])
        overlaps = overlaps / row['geometry'].area

        # if an RGI outline has more than 5% overlap, include it
        v7_outlines.loc[overlapping.loc[overlaps > 0.05].index, 'surge_type'] = row['SurgeType']

    v7_outlines.to_file(os.path.join('outlines', name_v7 + '.gpkg'))
