# -*- coding: utf-8 -*-
import geopandas as gpd, pandas as pd, numpy as np, json, sys
from pyproj import Transformer
sys.path.insert(0,'scripts')
from common import *

g = gpd.read_file('data/vetrovaly_3316.shp', where="region='Коми'")
g['geometry'] = g.geometry.make_valid()
g['year'] = g['date'].dt.year
g['period'] = (g['year']//5*5).map(lambda y: f'{y}–{y+4}')
g['area_ha'] = g['area'].round(1)

COMPASS = {'N':0,'NNE':22.5,'NE':45,'ENE':67.5,'E':90,'ESE':112.5,'SE':135,'SSE':157.5,
           'S':180,'SSW':202.5,'SW':225,'WSW':247.5,'W':270,'WNW':292.5,'NW':315,'NNW':337.5}
def parse_dir(d):
    if not isinstance(d,str) or '-' not in d: return (np.nan, np.nan)
    a,b = d.split('-')[:2]; a=a.strip().upper(); b=b.strip().upper()
    if a in COMPASS and b in COMPASS: return COMPASS[a], COMPASS[b]
    return (np.nan, np.nan)
g[['dir_from','dir_to']] = g['direction'].apply(lambda d: pd.Series(parse_dir(d)))

gp = g.to_crs(AEA)
inv = Transformer.from_crs(AEA, 4326, always_xy=True)
arrows=[]; heads=[]
for _, row in gp.iterrows():
    if pd.isna(row['dir_to']): continue
    geom = row.geometry
    poly = max(geom.geoms, key=lambda p: p.area) if hasattr(geom,'geoms') else geom
    if poly.is_empty or poly.area == 0: continue
    brng = np.deg2rad(row['dir_to']); ux, uy = np.sin(brng), np.cos(brng)
    pts = np.array(list(poly.exterior.coords) + [c for r in poly.interiors for c in r.coords])
    t = pts[:,0]*ux + pts[:,1]*uy
    tmin, tmax = float(t.min()), float(t.max()); span = tmax - tmin
    cx, cy = poly.centroid.x, poly.centroid.y; tc = cx*ux + cy*uy
    head_t = tmax - min(0.12*span, 900.0) - 120.0
    alen = min(max(2.6*np.sqrt(max(row['area'],1.0))*1000 + 6000, 10000), 42000)
    tail_t = head_t - alen
    if tail_t > tmin - 1200: tail_t = tmin - 1200
    def pt(tt):
        off = tt - tc; return (cx + off*ux, cy + off*uy)
    p0 = pt(tail_t); p1 = pt(head_t)
    lons, lats = inv.transform([p0[0], p1[0]], [p0[1], p1[1]])
    arrows.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[[round(lons[0],5),round(lats[0],5)],[round(lons[1],5),round(lats[1],5)]]},
                   'properties':{'id':int(row['id']), 'bearing': round(float(row['dir_to']),1), 'period': row['period']}})
    heads.append({'type':'Feature','geometry':{'type':'Point','coordinates':[round(lons[1],5),round(lats[1],5)]},
                  'properties':{'id':int(row['id']), 'bearing': round(float(row['dir_to']),1), 'period': row['period']}})
json.dump({'type':'FeatureCollection','features':arrows}, open('web/data/arrows.geojson','w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
json.dump({'type':'FeatureCollection','features':heads}, open('web/data/arrowheads.geojson','w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
print('arrows', len(arrows))
from collections import Counter
print(Counter(a['properties']['period'] for a in arrows))
