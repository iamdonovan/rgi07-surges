import os
import pandas as pd
import geopandas as gpd
import tools


# set the directory where the RGI folders are kept
rgi_dir = '/media/bob/seabox/RGI/'

all_regions = []
for rgn, name in tools.rgi7_namedict().items():
    surges = pd.read_csv(os.path.join('combined_attributes', tools.format_v7(rgn, name) + '.csv'))

    outlines = gpd.read_file(os.path.join(rgi_dir, 'v7b', tools.format_v7(rgn, name),
                                          tools.format_v7(rgn, name) + '.shp'))

    joined = outlines.merge(surges[['rgi_id', 'surge_type']], left_on='rgi_id', right_on='rgi_id')
    all_regions.append(joined)

combined_table = pd.concat(all_regions)
combined_table = combined_table.loc[combined_table['surge_type'].isin([1, 2, 3])]

combined_table['geometry'] = gpd.points_from_xy(combined_table['cenlon'], combined_table['cenlat'], crs='epsg:4326')
combined_table.to_file(os.path.join('data', 'joined_surges.gpkg'))

del combined_table['geometry']

combined_table.to_csv(os.path.join('data', 'final_surgetable.csv'), index=False)
