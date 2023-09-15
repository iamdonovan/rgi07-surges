import geopandas
import pandas
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

datapath = './data'

#import world map and glacier outlines for orientation
world = geopandas.read_file(os.path.join(datapath,'world.geo.json'))
gl_outlines = geopandas.read_file(os.path.join(datapath,'buffered_glacier_outlines/rgi60_buff_diss.shp'))

### Surge-type glaciers in RGI ###
rgi_attribs = pandas.concat(
    [pandas.read_csv(f, encoding='latin1') for f in glob.glob(os.path.join(datapath,'00_rgi60_attribs/*.csv'))],
    ignore_index = True
)
# Include all types ()
surges_rgi = rgi_attribs.loc[(rgi_attribs['Surging']==1) | (rgi_attribs['Surging']==2) | (rgi_attribs['Surging']==3)]

# turn surge points into a geodataframe for plotting
rgi_points = geopandas.GeoDataFrame(surges_rgi, geometry=geopandas.points_from_xy(surges_rgi.CenLon,surges_rgi.CenLat))

# Plot surge-type glaciers from RGI
f,ax = plt.subplots(figsize = (12,6))
world.plot(ax=ax, color='whitesmoke', edgecolor='silver', zorder=1)
rgi_points.plot(ax=ax, color='magenta', markersize=1.5, zorder=4)
gl_outlines.plot(ax=ax, color='skyblue', zorder=2)
ax.set_ylim([-60,90])
ax.set_xlim([-180,180])
ax.set_title(f"Surge-type glaciers from RGI-06 attribs (N={len(rgi_points)})" )
f.savefig('surges-RGI06.png', dpi=300)
#f.show()

### surge-type glaciers from Heidi's csv (ST_November.csv) ###
surges_heidi = pandas.read_csv(os.path.join(datapath,'ST_November.csv'))
heidi_points = geopandas.GeoDataFrame(
    surges_heidi,
    geometry=geopandas.points_from_xy(surges_heidi.CentLON,surges_heidi.CentLAT)
)

# Plot surge-type glaciers from file received from Heidi
f,ax = plt.subplots(figsize = (12,6))
world.plot(ax=ax, color='whitesmoke', edgecolor='silver', zorder=1)
heidi_points.plot(ax=ax, color='magenta', markersize=1.5, zorder=4)
gl_outlines.plot(ax=ax, color='skyblue', zorder=2)
ax.set_ylim([-60,90])
ax.set_xlim([-180,180])
ax.set_title(f"Surge-type glaciers from Sevestre & Benn (ST_November.csv; N={len(heidi_points)})")
f.savefig('surges-sevestre-benn.png', dpi=300)
#f.show()

### surge-type glaciers from geodatabaseSTglaciers ###

surges_gdb = pandas.read_csv(os.path.join(datapath,'GeodatabaseSTglaciers.csv'))
gdb_points = geopandas.GeoDataFrame(
    surges_gdb,
    geometry=geopandas.points_from_xy(surges_gdb.CENLON,surges_gdb.CENLAT)
)

# Plot surge-type glaciers from file received from GeodatabaseSTglaciers ###
f,ax = plt.subplots(figsize = (12,6))
world.plot(ax=ax, color='whitesmoke', edgecolor='silver', zorder=1)
gdb_points.plot(ax=ax, color='magenta', markersize=1.5, zorder=4)
gl_outlines.plot(ax=ax, color='skyblue', zorder=2)
ax.set_ylim([-60,90])
ax.set_xlim([-180,180])
ax.set_title(f"Surge-type glaciers from ?? Geodatabase (GeodatabaseSTglaciers; N={gdb_points.CENLAT.count()})")
f.savefig('surges-geodatabase.png', dpi=300)
#f.show()






