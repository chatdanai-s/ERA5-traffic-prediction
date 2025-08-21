import os
import cfgrib
import pandas as pd
import xarray as xr


year = 2013


# Ensure the script runs from the directory where it's located
os.chdir(os.path.dirname(__file__))

# Open the GRIB file using cfgrib
FILEPATH = 'ERA5_' + str(year) + '.grib'
# variables = ['t2m', 'tcc', 'lcc', 'mcc', 'hcc', 'ptype', 'tp', 'sf', 'cp', 'lsp']
variables = ['ptype', 'tp', 'sf', 'cp', 'lsp']
ds = []


# Load each variable separately and store in a list
DATA = xr.open_dataset(
        FILEPATH,
        engine='cfgrib',
        backend_kwargs={'filter_by_keys': {'edition': 1}}
        )
ds.append(DATA)

for var in variables:
    DATA = xr.open_dataset(
            FILEPATH,
            engine='cfgrib',
            backend_kwargs={'filter_by_keys': {'shortName': var}}
            )
    
    ds.append(DATA)     
    print(var)

# Convert datasets to appropriate dataframe
df0 = ds[0][['time', 't2m', 'tcc', 'lcc', 'mcc', 'hcc']].to_dataframe()
df1 = ds[1][['time', 'ptype']].to_dataframe()
df2 = ds[2][['time', 'tp']].to_dataframe()
df3 = ds[3][['time', 'sf']].to_dataframe()
df4 = ds[4][['time', 'cp']].to_dataframe()
df5 = ds[5][['time', 'lsp']].to_dataframe()

# Drop unused columns
columns_to_drop = ['number', 'step', 'surface']

for dataframes in [df0, df1, df2, df3, df4, df5]:
    dataframes.drop(columns=[col for col in columns_to_drop if col in dataframes.columns], inplace=True)


# Merge dataframes
df = pd.merge(df0, df1, on='valid_time', how='inner')
df = pd.merge(df, df2, on='valid_time', how='inner')
df = pd.merge(df, df3, on='valid_time', how='inner')
df = pd.merge(df, df4, on='valid_time', how='inner')
df = pd.merge(df, df5, on='valid_time', how='inner')


# Save as CSV file
df.to_csv('ERA5_' + str(year) + '.csv', index=False)
