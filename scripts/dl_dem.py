import urllib.request, os, concurrent.futures, time
os.makedirs(r'C:\grass_tmp\dem', exist_ok=True)
lats = range(58, 69)   # N58..N68
lons = range(45, 67)   # E045..E066
jobs=[]
for la in lats:
    for lo in lons:
        name=f'Copernicus_DSM_COG_30_N{la:02d}_00_E{lo:03d}_00_DEM'
        url=f'https://copernicus-dem-90m.s3.amazonaws.com/{name}/{name}.tif'
        dst=os.path.join(r'C:\grass_tmp\dem', name+'.tif')
        if not os.path.exists(dst) or os.path.getsize(dst)<1000000:
            jobs.append((url,dst))
print('jobs', len(jobs))
def get(j):
    url,dst=j
    for attempt in range(3):
        try:
            urllib.request.urlretrieve(url, dst+'.part')
            os.replace(dst+'.part', dst)
            return True
        except Exception as e:
            if attempt==2:
                print('FAIL', dst, e)
            time.sleep(1)
    return False
t=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    res=list(ex.map(get, jobs))
print('done', sum(res), 'in', round(time.time()-t,1),'s')
