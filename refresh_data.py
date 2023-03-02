import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


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


# first, copy the xlsx sheets to data/ in .csv format
glaciers = pd.read_excel('xlsx_docx/GeodatabaseSTglaciers.xlsx', sheet_name='Surge-type glaciers names')
surges = pd.read_excel('xlsx_docx/GeodatabaseSTglaciers.xlsx', sheet_name='Surges dates')

# join the glaciers and surge tables, but drop any columns with no name
joined = glaciers.set_index('Glacier_Name').join(surges.set_index('Glacier_Name'))
keep_cols = [c for c in joined.columns if 'Unnamed:' not in c]
joined = joined.loc[:, keep_cols]

# get the maximum surge index for each glacier
surge_index = joined.groupby('Glacier_Name')['Harmonised_Surge_Index'].max()

# for some reason, some glaciers don't have a value here - set to 1 (otherwise why is it in the table?)
surge_index[surge_index.isna()] = 1
joined['SurgeType'] = surge_index
joined.to_csv('data/GeodatabaseSTglaciers.csv', index=False)


november_df = pd.read_excel('xlsx_docx/ST_November.xlsx')
november_df['SurgeType'] = 1 # set to 1 by default, since we have no other information
november_df.to_csv('data/ST_November.csv', index=False)

# now, save the csv files as a gpkg
geodatabase = load_csv('data/GeodatabaseSTglaciers.csv', 'CENLON', 'CENLAT')
geodatabase.to_file('GeodatabaseSTglaciers.gpkg')

november = load_csv('data/ST_November.csv', 'CentLON', 'CentLAT')
november.to_file('ST_November.gpkg')


