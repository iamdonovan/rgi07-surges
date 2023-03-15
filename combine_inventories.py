import os
import pandas as pd
from glob import glob
import tools


# make the output folder if it doesn't exist
os.makedirs('combined_attributes', exist_ok=True)

# a dict of region numbers and names for RGI v7
namedict_v7 = tools.rgi7_namedict()

for rgn in namedict_v7.keys():
    name_v7 = tools.format_v7(rgn, namedict_v7[rgn])
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
