1
  2
  3
  4
  5
  6
  7
  8
  9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
 21
 22
 23
 24
 25
 26
 27
 28
 29
 30
 31
 32
 33
 34
 35
 36
 37
 38
 39
 40
 41
 42
 43
 44
 45
 46
 47
 48
 49
 50
 51
 52
 53
 54
 55
 56
 57
 58
 59
 60
 61
 62
 63
 64
 65
 66
 67
 68
 69
 70
 71
 72
 73
 74
 75
 76
 77
 78
 79
 80
 81
 82
 83
 84
 85
 86
 87
 88
 89
 90
 91
 92
 93
 94
 95
 96
 97
 98
 99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
import logging

import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import pandas as pd
from geovoronoi import coords_to_points, points_to_coords, voronoi_regions_from_coords
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
import os
from matplotlib.pyplot import figure
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzywuzzy.fuzz import ratio
import multiprocessing
import shutil 

plt.switch_backend('agg')
logging.basicConfig(level=logging.INFO)
geovoronoi_log = logging.getLogger('geovoronoi')
geovoronoi_log.setLevel(logging.INFO)
geovoronoi_log.propagate = True

arcdir="/data/eg-cluster-dir/eg-username/"
regdir="/Users/ollie/PakistanPoints/"

arc=True
if arc:
 dbf=arcdir+"/Pakistan Village Shapefile/PAK_Settlements_NGA_2017_20181122.dbf"
 shp=arcdir+"Admin Boundaries/District_Boundary.shp"
 pakistan_voronois = arcdir+"Pakistan Voronoi/"
else:
 dbf=regdir+"Pakistan Village Shapefile/PAK_Settlements_NGA_2017_20181122.dbf"
 shp=regdir+"Admin Boundaries/District_Boundary.shp"
 pakistan_voronois = regdir+"/Pakistan Voronoi/"

village=gpd.read_file(dbf)

village=village[village['PROVINCE']=="Punjab"]
village.DISTRICT=village.DISTRICT.str.upper()

areas=gpd.read_file(shp)
areas=areas[areas['PROVINCE']=='PUNJAB']
districts=[]
for i in areas.DISTRICT:
 districts.append(i)

threading=True

if threading:

 def doVoronoiForDistrict(districtNumber):
  i=districts[districtNumber-1]

  if i=="MUZAFARGARH":
   ii='MUZAFFARGARH'
  if i=="D G KHAN":
   ii='DERA GHAZI KHAN'
  if i=="T. T SINGH":
   ii='TOBA TEK SINGH'
  if i=="R Y KHAN":
   ii='RAHIM YAR KHAN'

  villages=village[village['DISTRICT']==i]
  if len(villages)==0:
   villages=village[village['DISTRICT']==ii]

  villages.reset_index(inplace=True)
  villages=villages.iloc[:10]
  coords = np.vstack((villages.LONG, villages.LAT)).T

  district=str(i)
  dist_dir=pakistan_voronois+district
  try:
   os.mkdir(dist_dir)
  except:
   shutil.rmtree(dist_dir, ignore_errors=True)
   os.mkdir(dist_dir)

  area=areas[areas['DISTRICT']==i]
  print('CRS:', area.crs)   # gives epsg:4326 -> WGS 84

  area_shape = area.iloc[0].geometry   # get the Polygon


  # use only the points inside the geographic area
  pts = [p for p in coords_to_points(coords) if p.within(area_shape)]  # converts to shapely Point


  coords = points_to_coords(pts)   # convert back to simple NumPy coordinate array
  #del pts

  #
  # calculate the Voronoi regions, cut them with the geographic area shape and assign the points to them
  #

  poly_shapes, pts, poly_to_pt_assignments = voronoi_regions_from_coords(coords, area_shape)
  villages.drop(columns={'geometry'}, inplace=True)
  villages['geometry'] = None


  count=-1
  #quit()
  for i in poly_to_pt_assignments:
   count=count+1
   try:
    for f in i:
     villages.loc[[f],'geometry']=poly_shapes[count]
     #print("polygon:",count,"point:", f)
   except:
    #print("skipped", "polygon:",count,"point:", f)
    pass

  villages.to_file(dist_dir+"/"+district+".dbf")
  fig, ax = subplot_for_map()
  plot_voronoi_polys_with_points_in_area(ax, area_shape, poly_shapes, coords, poly_to_pt_assignments)
  #plot_voronoi_polys_with_points_in_area(ax, area_shape, poly_shapes, coords)   # monocolor
  plt.tight_layout()
  plt.savefig(dist_dir+"/"+district+'.png',dpi=1000)

  return 
        
 p = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1)
 
 for i in p.imap_unordered(doVoronoiForDistrict, range(len(districts))):
     print(i)