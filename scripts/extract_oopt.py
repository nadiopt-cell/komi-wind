import lxml.etree as ET, lxml.html, re, html
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import unary_union
NS='{http://earth.google.com/kml/2.2}'
path=r'C:\grass_tmp\oopt_kmz\doc.kml'
rows=[]
for ev, el in ET.iterparse(path, events=('end',), tag=NS+'Placemark'):
    name = el.findtext(NS+'name') or ''
    folder = [a.findtext(NS+'name') or '' for a in el.iterancestors(NS+'Folder')]
    cat_folder = folder[0] if folder else ''
    desc = el.findtext(NS+'description') or ''
    attrs = {}
    if desc:
        try:
            doc = lxml.html.fromstring(html.unescape(desc))
            for tr in doc.iter('tr'):
                tds = [td.text_content().strip() for td in tr.findall('td')]
                if len(tds) == 2 and tds[0] and len(tds[0]) < 40 and len(tds[1]) < 300:
                    attrs[tds[0]] = tds[1]
        except Exception:
            pass
    rings=[]
    for cel in el.iter(NS+'coordinates'):
        if not cel.text: continue
        pts=[]
        for tok in cel.text.replace('\n',' ').split(' '):
            tok=tok.strip()
            if not tok: continue
            p=tok.split(',')
            if len(p)>=2:
                try: pts.append((float(p[0]), float(p[1])))
                except: pass
        if len(pts)>=4:
            if pts[0]==pts[-1]: pts=pts[:-1]
            if len(pts)>=3: rings.append(tuple(pts))
    geoms=[]
    for r in rings:
        try:
            pg=Polygon(r)
            if not pg.is_valid: pg=pg.buffer(0)
            if pg.area>0: geoms.append(pg)
        except Exception: pass
    if not geoms: continue
    # group separate polygons into multipolygon
    from shapely.geometry import MultiPolygon
    g = geoms[0] if len(geoms)==1 else MultiPolygon(geoms)
    rec = dict(name=name, cat_folder=cat_folder)
    for k in ('TITLE','SIG','CATEGORY','STATUS','AREA','REGION','NUMBER','EST_DATE'):
        if k in attrs: rec[k]=attrs[k]
    rec['geometry']=g
    rows.append(rec)
    el.clear()
print('parsed', len(rows))
gdf = gpd.GeoDataFrame(rows, crs=4326)
print('cols', gdf.columns.tolist())
gdf.to_file('data/oopt_raw.geojson', driver='GeoJSON')
print('written')
