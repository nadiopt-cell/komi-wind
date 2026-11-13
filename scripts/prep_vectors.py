import geopandas as gpd, pandas as pd, numpy as np, json, os
from shapely.geometry import LineString, MultiPolygon, Polygon
from pyproj import Transformer

WGS = 4326
AEA = '+proj=aea +lat_1=58 +lat_2=68 +lat_0=63 +lon_0=54 +datum=WGS84 +units=m +no_defs'
os.makedirs('web/data', exist_ok=True)

reg = gpd.read_file('data/osm/regions.gpkg')
komi = reg[reg['name_en'] == 'Komi Republic'].to_crs(WGS)
komi_geom = komi.geometry.union_all()

g = gpd.read_file('data/vetrovaly_3316.shp', where="region='Коми'")
g['geometry'] = g.geometry.make_valid()
g['year'] = g['date'].dt.year
g['period_start'] = (g['year'] // 5) * 5
labels = {y: f'{y}–{y+4}' for y in range(1980, 2030, 5)}
g['period'] = g['period_start'].map(labels)
g['area_ha'] = g['area'].round(1)

COMPASS = {'N':0,'NNE':22.5,'NE':45,'ENE':67.5,'E':90,'ESE':112.5,'SE':135,'SSE':157.5,
           'S':180,'SSW':202.5,'SW':225,'WSW':247.5,'W':270,'WNW':292.5,'NW':315,'NNW':337.5}
def parse_dir(d):
    if not isinstance(d,str) or '-' not in d: return (np.nan, np.nan)
    a,b = d.split('-')[:2]
    a=a.strip().upper(); b=b.strip().upper()
    if a in COMPASS and b in COMPASS:
        return COMPASS[a], COMPASS[b]
    return (np.nan, np.nan)
g[['dir_from','dir_to']] = g['direction'].apply(lambda d: pd.Series(parse_dir(d)))

gp = g.to_crs(AEA)
inv = Transformer.from_crs(AEA, WGS, always_xy=True)
arrows=[]; arrowheads=[]
for idx, row in gp.iterrows():
    if pd.isna(row['dir_to']):
        continue
    geom = row.geometry
    if hasattr(geom, 'geoms'):
        poly = max(geom.geoms, key=lambda p: p.area)
    else:
        poly = geom
    if poly.is_empty or poly.area == 0: continue
    brng = np.deg2rad(row['dir_to'])
    ux, uy = np.sin(brng), np.cos(brng)
    pts = np.array(list(poly.exterior.coords) + [c for r in poly.interiors for c in r.coords])
    t = pts[:,0]*ux + pts[:,1]*uy
    tmin, tmax = float(t.min()), float(t.max())
    span = tmax - tmin
    cx, cy = poly.centroid.x, poly.centroid.y
    tc = cx*ux + cy*uy
    head_t = tmax - min(0.12*span, 900.0) - 120.0
    alen = min(max(2.6*np.sqrt(max(row['area'],1.0))*1000 + 6000, 10000), 42000)
    tail_t = head_t - alen
    if tail_t > tmin - 1200:
        tail_t = tmin - 1200
    def pt(tt):
        off = tt - tc
        return (cx + off*ux, cy + off*uy)
    p0 = pt(tail_t); p1 = pt(head_t)
    lons, lats = inv.transform([p0[0], p1[0]], [p0[1], p1[1]])
    arrows.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[[lons[0],lats[0]],[lons[1],lats[1]]]},
                   'properties':{'id':int(row['id']), 'bearing': round(float(row['dir_to']),1), 'kind':'arrow'}})
    arrowheads.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lons[1],lats[1]]},
                       'properties':{'id':int(row['id']), 'bearing': round(float(row['dir_to']),1), 'kind':'head'}})

cols = ['id','type','date','year','period','area_ha','direction','path','district','place','dir_from','dir_to']
w = g[cols+['geometry']].copy()
w['date'] = w['date'].astype(str)
w['geometry'] = w.geometry.simplify(0.0006)
w.to_file('web/data/windfalls.geojson', driver='GeoJSON')
with open('web/data/arrows.geojson','w',encoding='utf-8') as f:
    json.dump({'type':'FeatureCollection','features':arrows}, f, ensure_ascii=False)
with open('web/data/arrowheads.geojson','w',encoding='utf-8') as f:
    json.dump({'type':'FeatureCollection','features':arrowheads}, f, ensure_ascii=False)
print('windfalls', len(w), 'arrows', len(arrows))

o = gpd.read_file('data/oopt_komi.geojson')
o = o[o.intersects(komi_geom)].copy()
o['geometry'] = o.geometry.intersection(komi_geom)
o = o[~o.geometry.is_empty]
o['area_km2'] = (o.to_crs(AEA).area/1e6).round(1)
o['geometry'] = o.geometry.simplify(0.001)
o['CATEGORY'] = o['CATEGORY'].fillna('прочее')
o[['name','CATEGORY','SIG','STATUS','area_km2','geometry']].to_file('web/data/oopt.geojson', driver='GeoJSON')
print('oopt', len(o))

r = gpd.read_file('data/osm/ne_rivers/ne_10m_rivers_lake_centerlines.shp')
r = r[r.intersects(komi_geom)].copy()
r['geometry'] = r.geometry.intersection(komi_geom.buffer(0.25))
r = r[~r.geometry.is_empty]
r['name_ru'] = r['name_ru'].fillna(r['name'])
r[['name','name_ru','scalerank','featurecla','geometry']].to_file('web/data/rivers.geojson', driver='GeoJSON')
print('rivers', len(r), r['name_ru'].tolist()[:20])

l = gpd.read_file('data/osm/ne_lakes/ne_10m_lakes.shp')
l = l[l.intersects(komi_geom.buffer(0.1))].copy()
l = l[l.geometry.area > 0.001]
l[['name','scalerank','geometry']].to_file('web/data/lakes.geojson', driver='GeoJSON')
print('lakes', len(l))

komi_s = komi.copy(); komi_s['geometry'] = komi_s.geometry.simplify(0.002)
komi_s[['name','name_en','iso','geometry']].to_file('web/data/komi.geojson', driver='GeoJSON')

print(g.groupby('period').agg(n=('id','size'), area=('area_ha','sum')).round(0).to_string())
print('total', len(g), 'ha', round(g['area_ha'].sum(),0))
print(g['type'].value_counts().to_string())
print('years', g['year'].min(), g['year'].max())
print('bounds', g.total_bounds)
