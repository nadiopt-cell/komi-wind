# common constants
import numpy as np
AEA = '+proj=aea +lat_1=58 +lat_2=68 +lat_0=63 +lon_0=54 +datum=WGS84 +units=m +no_defs'
MERC = 'EPSG:3857'
# master grid (AEA)
X0, Y0, X1, Y1 = -495000.0, -495000.0, 495000.0, 495000.0
RES = 150.0
W = int(round((X1-X0)/RES)); H = int(round((Y1-Y0)/RES))
# web mercator extent (comes from lon/lat)
WEB_LON = (45.45, 66.30)
WEB_LAT = (58.95, 68.50)
WEB_W = 5000

POSTER_DPI = 200
POSTER_W_PX = 4200
POSTER_H_PX = 5600

# 5-year periods & sequential ramp (old -> new)
PERIODS = ['1980–1984','1985–1989','1990–1994','1995–1999','2000–2004',
           '2005–2009','2010–2014','2015–2019','2020–2024','2025–2029']
PERIOD_START = [1980,1985,1990,1995,2000,2005,2010,2015,2020,2025]
# sequential, light sand -> deep plum
RAMP = ['#FCE9C8','#FBD49B','#F7B267','#F08A5D','#DE5F63','#C43F73','#A02C7C','#7A1C78','#521266','#2C0B3F']

FOREST_COLORS = {2: (46,107,79), 3: (126,154,78), 1: (201,162,39)}
