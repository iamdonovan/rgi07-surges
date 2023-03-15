import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf


# set the directory where the RGI folders are kept
rgi_dir = '/media/bob/seabox/RGI/'

global_data = pd.read_csv('data/final_surgetable.csv')

fig = plt.figure(figsize=(18, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

ax.add_feature(cf.LAND, facecolor='whitesmoke')
ax.add_feature(cf.LAKES, facecolor='white', edgecolor='k', linewidth=0.2)
ax.add_feature(cf.BORDERS, linewidth=0.2)
ax.coastlines(resolution='50m', linewidth=0.2)

gl_outlines = gpd.read_file('data/buffered_glacier_outlines/rgi60_buff_diss.shp')

global_outlines = cf.ShapelyFeature(gl_outlines['geometry'], ccrs.PlateCarree(), edgecolor='none', facecolor='skyblue')
ax.add_feature(global_outlines)

ax.plot(global_data.loc[global_data.surge_type == 1, 'cenlon'],
        global_data.loc[global_data.surge_type == 1, 'cenlat'], 'o', ms=2, color='palevioletred', label='possible',
        transform=ccrs.PlateCarree())

ax.plot(global_data.loc[global_data.surge_type == 2, 'cenlon'],
        global_data.loc[global_data.surge_type == 2, 'cenlat'], 'o', ms=2, color='coral', label='probable',
        transform=ccrs.PlateCarree())

ax.plot(global_data.loc[global_data.surge_type == 3, 'cenlon'],
        global_data.loc[global_data.surge_type == 3, 'cenlat'], 'o', ms=2, color='magenta', label='observed',
        transform=ccrs.PlateCarree())

ax.legend(fontsize=14, loc='lower left', markerscale=4)
ax.set_ylim(-85, 85)
ax.set_xlim(-180, 180)

fig.savefig('combined_distribution.png', dpi=300, bbox_inches='tight')
