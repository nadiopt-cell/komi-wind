import json
pts=[{"name":"Югыд Ва","lon":59.35,"lat":64.15},{"name":"Печоро-Илычский","lon":58.55,"lat":62.05}]
feats=[{'type':'Feature','properties':{'name':p['name']},'geometry':{'type':'Point','coordinates':[p['lon'],p['lat']]}} for p in pts]
json.dump({'type':'FeatureCollection','features':feats}, open('web/data/oopt_labels.geojson','w',encoding='utf-8'), ensure_ascii=False)
print('ok')
