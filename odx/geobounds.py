import pandas as pd
import geopandas as gpd
import warnings


link = "CT2010.geojson"
gdf = gpd.read_file(link)
gdf_bounds = gpd.GeoDataFrame(gdf.bounds) #geopandas.bounds selects the max and min values of log/lat in each multipolygon


'''
UNCOMMENT TO VISUALIZE CENSUS TRACT BOUNDS
'''
# import matplotlib.pyplot as plt
# warnings.filterwarnings('ignore')
# plt.style.use('bmh')
# gdf.plot()
# gdf_bounds.plot()
# plt.show()

'''
Convert bounded tracts to dataframe and save a pdf
'''
df_original = pd.DataFrame(gdf)
df_original['geometry'] = df_original['geometry'].apply(lambda g: g.wkt)

df_bounds = pd.DataFrame(gdf_bounds)
result = pd.concat([df_original, df_bounds], axis=1)

result.to_csv('census_tracts_bounded.csv')
