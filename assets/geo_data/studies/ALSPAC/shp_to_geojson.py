# convert shp to geojson
import geopandas
#import os
#import shapefile
#os.chdir("L:/Data/geo_data/studies/ALSPAC")

# METHOD 1 - geopandas
shp_file = geopandas.read_file('L:/Data/geo_data/studies/ALSPAC/DHAs/Eligible_1991_DHAs.shp')
shp_file.to_file('L:/Data/geo_data/studies/ALSPAC/ALSPAC_eligible_DHAs.geojson', driver='GeoJSON')

# METHOD 2 - 
#with shapefile.Reader('Eligible_1991_DHA.shp') as shp:
#    geojson_data = shp.__geo_interface__