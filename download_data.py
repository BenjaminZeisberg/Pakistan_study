import pandas as pd
import numpy as np
import geopandas as gpd

# We have our data in the df
helena = pd.read_csv('data/helena_tehsil.csv')

# view and merge files
helena = pd.read_csv('helena_tehsils_correct.csv')
helena['Correct_Tehsil'] = helena['Correct_Tehsil'].apply(lambda x: x.lower())

# Get the polygon shapes
table = gpd.read_file('coordinates/adm3/geoBoundaries-PAK-ADM3.dbf')
df_adm3 = pd.DataFrame(table)

polygons = df_adm3[['shapeName', 'geometry']]
polygons['shapeName'] = polygons['shapeName'].apply(lambda x: x.lower())

# Select Tehsils of interest
df_adm3['shapeName'] = df_adm3['shapeName'].apply(lambda x: x.lower())
common = list(set(helena['Correct_Tehsil']).intersection(df_adm3['shapeName']))
teh_interest = df_adm3[df_adm3['shapeName'].isin(common)]

