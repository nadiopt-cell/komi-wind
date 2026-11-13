import urllib.request, os
ranges=['0-255','256-511','1024-1279','1280-1535','7936-8191']
H={'User-Agent':'Mozilla/5.0'}
for stack in ['Noto Sans Regular','Noto Sans Bold']:
    d=os.path.join('web','vendor','fonts',stack)
    os.makedirs(d,exist_ok=True)
    for rg in ranges:
        url=f'https://demotiles.maplibre.org/font/{stack.replace(" ","%20")}/{rg}.pbf'
        dst=os.path.join(d, rg+'.pbf')
        try:
            r=urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60)
            open(dst,'wb').write(r.read())
            print(dst, os.path.getsize(dst))
        except Exception as e:
            print('ERR',url,e)
