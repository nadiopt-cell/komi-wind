import geopandas as gpd, numpy as np, sys
sys.path.insert(0,'scripts')
from common import *
a=gpd.read_file('web/data/arrows.geojson').to_crs(AEA)
L=a.length/1000
print('arrows', len(L))
print('min/med/mean/max km', round(L.min(),1), round(L.median(),1), round(L.mean(),1), round(L.max(),1))
for ha in [5,10,30,80,300,1000,3000,6221]:
    f=min(max(2.6*np.sqrt(ha)*1000+6000,10000),42000)/1000
    print(ha,'ha ->', round(f,1),'km')
w=gpd.read_file('web/data/windfalls.geojson')
w['alen']=[f for f in L]
print(w[['area_ha','path','alen']].describe().round(1).to_string())
