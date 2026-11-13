import urllib.request, os, concurrent.futures
os.makedirs(r'C:\grass_tmp\dem', exist_ok=True)
jobs=[]
for la in range(56,71):
    for lo in range(43,68):
        name=f'Copernicus_DSM_COG_30_N{la:02d}_00_E{lo:03d}_00_DEM'
        url=f'https://copernicus-dem-90m.s3.amazonaws.com/{name}/{name}.tif'
        dst=os.path.join(r'C:\grass_tmp\dem', name+'.tif')
        if not os.path.exists(dst) or os.path.getsize(dst)<1000000:
            jobs.append((url,dst))
print('missing', len(jobs))
def get(j):
    url,dst=j
    try:
        urllib.request.urlretrieve(url, dst+'.part'); os.replace(dst+'.part',dst); return True
    except Exception:
        return False
with concurrent.futures.ThreadPoolExecutor(max_workers=14) as ex:
    res=list(ex.map(get,jobs))
print('ok', sum(res))
print('total tiles', len([f for f in os.listdir(r'C:\grass_tmp\dem') if f.endswith('.tif')]))
