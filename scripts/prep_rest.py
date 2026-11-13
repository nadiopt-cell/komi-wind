import geopandas as gpd
from shapely import make_valid
reg = gpd.read_file('data/osm/regions.gpkg')
k = reg[reg['name_en']=='Komi Republic'].to_crs(4326).copy()
kg = make_valid(k.geometry.union_all())
print('valid', kg.is_valid, kg.geom_type, round(kg.area,3))
out = gpd.GeoDataFrame({'name':['Республика Коми'],'name_en':['Komi Republic'],'iso':['RU-KO']}, geometry=[kg], crs=4326)
out['geometry'] = out.geometry.simplify(0.002)
out.to_file('web/data/komi.geojson', driver='GeoJSON')
print(out.total_bounds)

o = gpd.read_file('data/oopt_komi.geojson')
o['geometry'] = o.geometry.apply(make_valid)
o = o[o.intersects(kg)].copy()
o['geometry'] = o.geometry.apply(lambda g: make_valid(g.intersection(kg)))
o = o[~o.geometry.is_empty]
AEA='+proj=aea +lat_1=58 +lat_2=68 +lat_0=63 +lon_0=54 +datum=WGS84 +units=m +no_defs'
o['area_km2'] = (o.to_crs(AEA).area/1e6).round(1)
o['geometry'] = o.geometry.apply(lambda g: g.simplify(0.001))
o['CATEGORY'] = o['CATEGORY'].fillna('прочее')
o[['name','CATEGORY','SIG','STATUS','area_km2','geometry']].to_file('web/data/oopt.geojson', driver='GeoJSON')
print('oopt kept', len(o), o['CATEGORY'].value_counts().to_dict())

r = gpd.read_file('data/osm/ne_rivers/ne_10m_rivers_lake_centerlines.shp')
r = r[r.intersects(kg)].copy()
r['geometry'] = r.geometry.apply(lambda g: make_valid(g.intersection(kg.buffer(0.25))))
r = r[~r.geometry.is_empty]
r['name_ru'] = r['name_ru'].fillna(r['name'])
r[['name','name_ru','scalerank','featurecla','geometry']].to_file('web/data/rivers.geojson', driver='GeoJSON')
print('rivers', len(r), r['name_ru'].tolist())

l = gpd.read_file('data/osm/ne_lakes/ne_10m_lakes.shp')
l = l[l.intersects(kg.buffer(0.1))].copy()
l = l[l.geometry.area>0.001]
l[['name','scalerank','geometry']].to_file('web/data/lakes.geojson', driver='GeoJSON')
print('lakes', len(l))
