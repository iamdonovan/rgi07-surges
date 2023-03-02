import os
import pandas as pd
from glob import glob


def format_v7(rgn, name):
    """
    Given a region and a name, construct the RGI v7 region name for a file/folder

    :param str rgn: the region number (e.g., '01')
    :param str name: the region name (e.g., 'alaska')
    :return:
    """
    return '-'.join(['RGI2000', 'v7.0', 'G', '_'.join([rgn, name.lower()])])


# make the output folder if it doesn't exist
os.makedirs('combined_attributes', exist_ok=True)

# get a list of region numbers, formatted as 2-digit strings
regions = ['{:02d}'.format(n) for n in range(1, 20)]

# the list of region names used in RGI v7
names_v7 = ['alaska', 'western_canada_usa', 'arctic_canada_north', 'arctic_canada_south', 'greenland_periphery',
            'iceland', 'svalbard_jan_mayen', 'scandinavia', 'russian_arctic', 'asia_north',
            'central_europe', 'caucasus_middle_east', 'asia_central', 'asia_south_west', 'asia_south_east',
            'low_latitudes', 'southern_andes', 'new_zealand', 'subantarctic_antarctic_islands']
# a dict of region numbers and names for RGI v7
namedict_v7 = dict(zip(regions, names_v7))

for rgn in regions:
    name_v7 = format_v7(rgn, namedict_v7[rgn])
    print(name_v7)

    csvlist = glob(os.path.join('attributes', name_v7) + '*.csv')
    csvlist.sort()

    rgn_data = []

    for fn_csv in csvlist:
        this_csv = pd.read_csv(fn_csv)

        # get the source name from the filename
        src_name = os.path.splitext(os.path.basename(fn_csv))[0].split('_')[-1]

        # rename the surge_type column to include the source
        this_csv.rename(columns={'surge_type': '_'.join(['surge_type', src_name])}, inplace=True)

        # set the index to the rgi id
        rgn_data.append(this_csv.set_index('rgi_id'))

    # combine the different datasets for this region
    rgn_data = pd.concat(rgn_data, axis=1)

    # make sure that "unknown" isn't the maximum
    rgn_data[rgn_data == 9] = -1

    # get the maximum value in each row, column-wise
    rgn_data['surge_type'] = rgn_data[rgn_data.columns].max(axis=1)

    # set "unknown" back to 9
    rgn_data[rgn_data == -1] = 9

    rgn_data.to_csv(os.path.join('combined_attributes', name_v7 + '.csv'))
