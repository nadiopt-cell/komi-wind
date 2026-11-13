import geopandas as gpd, numpy as np, sys
sys.path.insert(0,'scripts')
from common import *
w = gpd.read_file('web/data/windfalls.geojson').to_crs(AEA)
o = gpd.read_file('web/data/oopt.geojson').to_crs(AEA)
x = np.array([g.centroid.x for g in w.geometry]); y = np.array([g.centroid.y for g in w.geometry])
a = w['area_ha'].values
best=None
for cx in range(int(x.min()), int(x.max()), 25000):
    for cy in range(int(y.min()), int(y.max()), 25000):
        m = (np.abs(x-cx)<60000)&(np.abs(y-cy)<60000)
        sc = a[m].sum()
        if best is None or sc>best[0]: best=(sc,cx,cy,m.sum())
print('best 120x120 window', best)
sc,cx,cy,n = best
m=(np.abs(x-cx)<60000)&(np.abs(y-cy)<60000)
sub=w[m]
print(sub[['id','year','area_ha','direction','district']].sort_values('area_ha',ascending=False).head(10).to_string())
print('events',n,'area',sub['area_ha'].sum())
# oopt overlap
pt = gpd.GeoSeries(gpd.points_from_xy(x,y), crs=AEA)
for i,row in o.iterrows():
    if row.geometry.intersects(__import__('shapely').box(cx-60000,cy-60000,cx+60000,cy+60000)):
        print('OOPT', row['name'], row['area_km2'])
