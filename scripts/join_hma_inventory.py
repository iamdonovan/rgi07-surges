import os
import geopandas as gpd
import pandas as pd
import numpy as np
import tools


# make the output folder if it doesn't exist
os.makedirs('attributes', exist_ok=True)

# set the directory where the RGI folders are kept
rgi_dir = '/media/bob/seabox/RGI/'

# step 1: load the csv
hma_inventory = pd.read_csv('HMA_STG_inventory-v1/surge_inventory.csv')

hma_inventory['SurgeType'] = 2 # set to probable by default
# if consecutive years > 0, it's "observed"
hma_inventory.loc[hma_inventory['consec_surging_years'] > 0, 'SurgeType'] = 3

# this inventory covers regions 13, 14, and 15
regions = ['{:02d}'.format(n) for n in range(13, 16)]

# the list of region names used in RGI v7
names_v7 = ['asia_central', 'asia_south_west', 'asia_south_east']
# a dict of region numbers and names for RGI v7
namedict_v7 = dict(zip(regions, names_v7))

# the list of region names used in RGI v6
names_v6 = ['CentralAsia', 'SouthAsiaWest', 'SouthAsiaEast']
# a dict of region numbers and names for RGI v6
namedict_v6 = dict(zip(regions, names_v6))

for reg in regions:
    name_v7 = tools.format_v7(reg, namedict_v7[reg])
    print(name_v7)

    name_v6 = tools.format_v6(reg, namedict_v6[reg])

    # load the RGI7 and RGI6 outlines
    v7_outlines = gpd.read_file(os.path.join(rgi_dir, 'v7b', name_v7, name_v7 + '.shp'))
    v6_outlines = gpd.read_file(os.path.join(rgi_dir, 'v6.0', name_v6, name_v6 + '.shp'))

    # join the inventory to the RGI6 outlines
    hma_joined = gpd.GeoDataFrame(hma_inventory.set_index('RGIId').join(v6_outlines.set_index('RGIId'), lsuffix='inv'))
    hma_joined.dropna(subset='geometry', inplace=True)
    hma_joined['RGIId'] = hma_joined.index

    overlap = v7_outlines.sjoin(hma_joined)

    # should probably convert to a projected CRS for this...
    for ind, row in hma_joined.iterrows():
        # get all of the outlines that overlap with this one
        overlapping = overlap.loc[overlap['RGIId'] == ind]

        # get the fraction of this outline's area that each overlap equals
        overlaps = np.array([row['geometry'].intersection(o['geometry']).area for _, o in overlapping.iterrows()])
        overlaps = overlaps / row['geometry'].area

        # if an RGI outline has more than 5% overlap, include it
        v7_outlines.loc[overlapping.loc[overlaps > 0.05].index, 'surge_type'] = row['SurgeType']

    v7_outlines[['rgi_id', 'surge_type']].to_csv(os.path.join('attributes', name_v7 + '_hma.csv'), index=False)
