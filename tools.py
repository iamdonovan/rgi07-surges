import geopandas as gpd
import pandas as pd


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

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col], crs='epsg:4326'))

    return gdf


def join_attrs(outlines, points, data_name, colname='SurgeType'):
    """
    Use a spatial join to join points to outlines, then add the value of the "Surging" column from the points based
    on the

    :param GeoDataFrame outlines: The outlines to add an attribute to
    :param GeoDataFrame points: The points to use to add attributes
    :param str data_name: the name of the dataset, for keeping track of where missing glaciers come from.
    :param str colname: the name of the column that contains the surgetype attribute
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
    unique = joined.drop_duplicates(subset=['index_right'])

    # now, make sure we have the maximal surge_type value for each point
    for ind, row in unique.iterrows():
        dups = joined.loc[joined['index_right'] == row['index_right']]
        unique.loc[ind, 'SurgeType'] = dups[colname].max()

    # now, get the rows that matched
    is_matched = outlines.index.isin(unique['index_right'])
    # set the RGI v6 surge flag to equal what we get out of the joined table
    outlines.loc[is_matched, 'surge_type'] = outlines.join(unique.set_index('index_right'), lsuffix='_')['SurgeType']

    return outlines, missing


def rgi7_namedict():
    # get a list of region numbers, formatted as 2-digit strings
    regions = ['{:02d}'.format(n) for n in range(1, 20)]

    # the list of region names used in RGI v7
    names = ['alaska', 'western_canada_usa', 'arctic_canada_north', 'arctic_canada_south', 'greenland_periphery',
             'iceland', 'svalbard_jan_mayen', 'scandinavia', 'russian_arctic', 'asia_north',
             'central_europe', 'caucasus_middle_east', 'asia_central', 'asia_south_west', 'asia_south_east',
             'low_latitudes', 'southern_andes', 'new_zealand', 'subantarctic_antarctic_islands']
    # a dict of region numbers and names for RGI v7
    namedict = dict(zip(regions, names))
    return namedict
