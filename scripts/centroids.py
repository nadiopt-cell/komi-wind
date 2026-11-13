import geopandas as gpd, json, sys, numpy as np
sys.path.insert(0,'scripts')
from common import *
w=gpd.read_file('web/data/windfalls.geojson').to_crs(AEA)
c=w.geometry.centroid.to_crs(4326)
feats=[]
for (i,row),g in zip(w.iterrows(), c):
    feats.append({'type':'Feature','properties':{'id':int(row['id']),'period':row['period'],'area_ha':float(row['area_ha'])},
                  'geometry':{'type':'Point','coordinates':[round(g.x,4),round(g.y,4)]}})
json.dump({'type':'FeatureCollection','features':feats}, open('web/data/wf_centroids.geojson','w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
print('ok', len(feats))
