import pandas as pd, numpy as np, geopandas as gpd, json, os
from shapely.geometry import LineString, MultiLineString
d = pd.read_pickle('data/osm/rivers_compact.pkl')
segs = d['segments']; widths = d['widths']
geoms = [LineString(np.asarray(s)) for s in segs if len(s) >= 2]
g = gpd.GeoDataFrame({'width': widths[:len(geoms)]}, geometry=geoms, crs=3857)
print('rivers', len(g), g['width'].value_counts().to_dict())
g.to_file('build/rivers_osm.gpkg', layer='rivers', driver='GPKG')

# web version: width>=0.6, simplify 120 m
w = g[g['width'] >= 0.6].copy()
w['geometry'] = w.geometry.simplify(120)
w = w.to_crs(4326)
w['w'] = w['width'].round(2)
w[['w','geometry']].to_file('web/data/rivers_osm.geojson', driver='GeoJSON')
print('web rivers', len(w), os.path.getsize('web/data/rivers_osm.geojson')/1e6, 'MB')

l = gpd.read_file('data/osm/lakes_compact.gpkg')
l = l[l.geometry.area > 1.0e6]  # >1 km2
l = l.to_crs(4326)
l['geometry'] = l.geometry.simplify(0.001)
l[['name','geometry']].to_file('web/data/lakes_osm.geojson', driver='GeoJSON')
l.to_file('build/lakes_osm.gpkg', driver='GPKG')
print('lakes', len(l), os.path.getsize('web/data/lakes_osm.geojson')/1e6, 'MB')
print(l['name'].dropna().head(20).tolist())
