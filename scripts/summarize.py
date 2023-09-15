import os
import pandas as pd
import tools


# get the RGI v7 namedict
namedict_v7 = tools.rgi7_namedict()

summary = pd.DataFrame()

for ind, rgn in enumerate(namedict_v7.keys()):
    summary.loc[ind, 'region'] = namedict_v7[rgn]

    attrs = pd.read_csv(os.path.join('combined_attributes', tools.format_v7(rgn, namedict_v7[rgn]) + '.csv'))

    summary.loc[ind, 'nglac'] = attrs.shape[0]
    summary.loc[ind, 'observed'] = attrs.loc[attrs['surge_type'] == 3].shape[0]
    summary.loc[ind, 'probable'] = attrs.loc[attrs['surge_type'] == 2].shape[0]
    summary.loc[ind, 'possible'] = attrs.loc[attrs['surge_type'] == 1].shape[0]

# get the totals for all regions
summary.loc[19, 'region'] = 'total'
summary.loc[19, 'nglac'] = summary['nglac'].sum()
summary.loc[19, 'observed'] = summary['observed'].sum()
summary.loc[19, 'probable'] = summary['probable'].sum()
summary.loc[19, 'possible'] = summary['possible'].sum()

# get the total for each region
summary['total'] = summary[['observed', 'probable', 'possible']].sum(axis=1)

# make it into an integer, rather than a float
summary = summary.set_index('region').astype(int)
summary.to_csv('regional_summary.csv')

print(summary)

