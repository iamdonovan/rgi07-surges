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
geodatabase_df = pd.read_excel('xlsx_docx/GeodatabaseSTglaciers.xlsx', sheet_name='Surge-type glaciers names')
geodatabase_df.to_csv('data/GeodatabaseSTglaciers.csv', index=False)

november_df = pd.read_excel('xlsx_docx/ST_November.xlsx')
november_df.to_csv('data/ST_November.csv', index=False)

# now, save the csv files as a gpkg
geodatabase = load_csv('data/GeodatabaseSTglaciers.csv', 'CENLON', 'CENLAT')
geodatabase.to_file('GeodatabaseSTglaciers.gpkg')

november = load_csv('data/ST_November.csv', 'CentLON', 'CentLAT')
november.to_file('ST_November.gpkg')


