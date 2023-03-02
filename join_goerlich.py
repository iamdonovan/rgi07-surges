import os
import geopandas as gpd
import pandas as pd
import numpy as np


# make the output folder if it doesn't exist
os.makedirs('attributes', exist_ok=True)

goerlich_outlines = gpd.read_file('Goerlich_2020/Goerlich_2020_GI-3/GI-3_rev.shp')

# goerlich's outlines are only within RGI region 13
rgi_dir = '/media/bob/seabox/RGI/'
region = 'RGI2000-v7.0-G-13_asia_central'
rgi_outlines = gpd.read_file(os.path.join(rgi_dir, 'v7b', region, region + '.shp'))

# overlapping glaciers (to cut down on searching by distance later)
overlap = rgi_outlines.sjoin(goerlich_outlines.to_crs(epsg=4326))
overlap.to_crs(goerlich_outlines.crs, inplace=True)

for ind, row in goerlich_outlines.iterrows():
    # get all of the outlines that overlap with this one
    overlapping = overlap.loc[overlap['glac_id'] == row['glac_id']]

    # get the fraction of this outline's area that each overlap equals
    overlaps = np.array([row['geometry'].intersection(o['geometry']).area for _, o in overlapping.iterrows()])
    overlaps = overlaps / row['geometry'].area

    # if an RGI outline has more than 5% overlap, include it
    rgi_outlines.loc[overlapping.loc[overlaps > 0.05].index, 'surge_type'] = 3

rgi_outlines[['rgi_id', 'surge_type']].to_csv(os.path.join('attributes', region + '_goerlich.csv'), index=False)
