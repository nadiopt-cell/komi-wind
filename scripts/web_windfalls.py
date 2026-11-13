import geopandas as gpd, json, numpy as np, sys, os
sys.path.insert(0,'scripts')
from common import *
def rnd(o, nd=5):
    if isinstance(o,(list,tuple)): return [rnd(v,nd) for v in o]
    if isinstance(o,float): return round(o,nd)
    return o
w = gpd.read_file('data/vetrovaly_3316.shp', where="region='Коми'")
w['geometry']=w.geometry.make_valid()
w['year']=w['date'].dt.year
w['period']=(w['year']//5*5).map(lambda y: f'{y}–{y+4}')
w['area_ha']=w['area'].round(1)
w=w.to_crs(AEA); w['geometry']=w.geometry.simplify(35,preserve_topology=True); w=w.to_crs(4326)
feats=[]
for _,r in w.iterrows():
    d=r.geometry.__geo_interface__
    feats.append({'type':'Feature','properties':{
        'id':int(r['id']),'type':r['type'],'year':int(r['year']),'period':r['period'],
        'area_ha':round(float(r['area_ha']),1),'direction':r['direction'] if isinstance(r['direction'],str) else '',
        'path':float(r['path']) if r['path']==r['path'] else None,
        'district':r['district'] if isinstance(r['district'],str) else '',
        'date':str(r['date'])[:10]},
        'geometry':{'type':d['type'],'coordinates':rnd(d['coordinates'],5)}})
json.dump({'type':'FeatureCollection','features':feats}, open('web/data/windfalls.geojson','w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
print('ok', round(os.path.getsize('web/data/windfalls.geojson')/1e6,2),'MB')
