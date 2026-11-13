import geopandas as gpd, json, numpy as np, sys, os
from shapely.geometry import MultiPolygon, Polygon
sys.path.insert(0,'scripts')
from common import *
def rnd(o, nd=4):
    if isinstance(o,(list,tuple)): return [rnd(v,nd) for v in o]
    if isinstance(o,float): return round(o,nd)
    return o
def write_gj(gdf, path, nd=4, props=None):
    feats=[]
    for _, row in gdf.iterrows():
        g=row.geometry
        if g is None or g.is_empty: continue
        d=g.__geo_interface__
        pr={}
        for k in (props or [c for c in gdf.columns if c!='geometry']):
            v=row[k]
            if isinstance(v,(np.integer,)): v=int(v)
            elif isinstance(v,(np.floating,)): v=round(float(v),2)
            if isinstance(v,float) and v!=v: v=None
            pr[k]=v
        feats.append({'type':'Feature','properties':pr,'geometry':{'type':d['type'],'coordinates':rnd(d['coordinates'],nd)}})
    json.dump({'type':'FeatureCollection','features':feats}, open(path,'w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
    print(path, round(os.path.getsize(path)/1e6,2),'MB', len(feats))

# --- windfalls: simplify 70m, drop tiny parts ---
w = gpd.read_file('data/vetrovaly_3316.shp', where="region='Коми'")
w['geometry']=w.geometry.make_valid()
w['year']=w['date'].dt.year
w['period']=(w['year']//5*5).map(lambda y: f'{y}–{y+4}')
w['area_ha']=w['area'].round(1)
w['date']=w['date'].astype(str)
w=w.to_crs(AEA)
def clean(g):
    parts=[p for p in (g.geoms if g.geom_type=='MultiPolygon' else [g]) if p.area>10000]  # >1 ha
    if not parts: parts=[max((g.geoms if g.geom_type=='MultiPolygon' else [g]), key=lambda p:p.area)]
    g2=MultiPolygon(parts) if len(parts)>1 else parts[0]
    return g2.simplify(70, preserve_topology=True)
w['geometry']=[clean(g) for g in w.geometry]
pts=sum((len(p.exterior.coords) for g in w.geometry for p in (g.geoms if g.geom_type=='MultiPolygon' else [g])),0)
print('windfall vertices', pts)
w=w.to_crs(4326)
write_gj(w,'web/data/windfalls.geojson',4,props=['id','type','year','period','area_ha','direction','path','district','date'])

# --- rivers: major only ---
r=gpd.read_file('build/rivers_osm.gpkg')
r=r[r['width']>=0.8].copy()
r['geometry']=r.geometry.simplify(300, preserve_topology=False)
r=r.to_crs(4326)
write_gj(r,'web/data/rivers_osm.geojson',4,props=['width'])

# --- lakes ---
l=gpd.read_file('build/lakes_osm.gpkg')
l['geometry']=l.geometry.simplify(400, preserve_topology=True)
write_gj(l.to_crs(4326),'web/data/lakes_osm.geojson',4,props=[])

# --- oopt ---
o=gpd.read_file('web/data/oopt.geojson').to_crs(AEA)
o['geometry']=o.geometry.simplify(150, preserve_topology=True)
write_gj(o.to_crs(4326),'web/data/oopt.geojson',4,props=['name','CATEGORY','SIG','STATUS','area_km2'])
