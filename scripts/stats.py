import geopandas as gpd, numpy as np, json, sys, rasterio
sys.path.insert(0,'scripts')
from common import *
w = gpd.read_file('web/data/windfalls.geojson')
o = gpd.read_file('web/data/oopt.geojson')
w_m = w.to_crs(AEA); o_m = o.to_crs(AEA)
A = w['area_ha'].sum()
print('events', len(w), 'area ha', round(A))
print(w.groupby('period').agg(n=('id','size'), area=('area_ha','sum')).round(0).to_string())
print('types'); print(w.groupby('type').agg(n=('id','size'), area=('area_ha','sum')).round(0).to_string())
oo = o_m.geometry.union_all()
inter = w_m.geometry.intersection(oo)
w_m['oopt_ha'] = inter.area/1e4
print('in oopt area ha', round(w_m['oopt_ha'].sum()), 'share', round(100*w_m['oopt_ha'].sum()/A,1), '%')
print('events touching oopt', (w_m['oopt_ha']>0.01).sum())

dem = np.load('build/dem.npy')
from rasterio.features import geometry_mask
from rasterio.transform import from_origin as fo
def elev_of(g):
    b = g.bounds
    c0 = max(0,int((b[0]-X0)/RES)); c1 = min(W,int((b[2]-X0)/RES)+1)
    r0 = max(0,int((Y1-b[3])/RES)); r1 = min(H,int((Y1-b[1])/RES)+1)
    if c1<=c0 or r1<=r0: return np.nan
    sub = dem[r0:r1, c0:c1]
    m = geometry_mask([g], out_shape=sub.shape, transform=fo(X0+c0*RES, Y1-r0*RES, RES, RES), invert=True)
    if m.sum()==0: return np.nan
    return float(np.median(sub[m]))
w_m['elev'] = [elev_of(g) for g in w_m.geometry]
print(w_m['elev'].describe().round(0).to_string())
w_m['eb']=np.digitize(w_m['elev'], [100,200,300,400,600])
print(w_m.groupby('eb').agg(n=('id','size'), area=('area_ha','sum'), e=('elev','median')).round(0).to_string())

def grp(d):
    if d != d: return 'н/д'
    if 247.5 <= d <= 292.5: return 'З'
    if 202.5 <= d < 247.5: return 'ЮЗ'
    if 157.5 <= d < 202.5: return 'Ю'
    if d >= 337.5 or d < 22.5: return 'С'
    if 22.5 <= d < 67.5: return 'СВ'
    if 67.5 <= d < 112.5: return 'В'
    if 112.5 <= d < 157.5: return 'ЮВ'
    return 'СЗ'
w['dir_group'] = w['dir_from'].map(grp)
print(w['dir_group'].value_counts().to_string())
print('share W/SW/NW', round(100*w['dir_group'].isin(['З','ЮЗ','СЗ']).mean(),1))
print(w.sort_values('area_ha',ascending=False).head(5)[['id','year','area_ha','direction','district']].to_string())
print(w.groupby('district').agg(n=('id','size'), area=('area_ha','sum')).sort_values('area',ascending=False).head(6).round(0).to_string())
w_m.to_file('build/windfalls_stats.gpkg', driver='GPKG')
