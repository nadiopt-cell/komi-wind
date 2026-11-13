import urllib.request, os, shutil, time
url='https://zenodo.org/records/3939050/files/PROBAV_LC100_global_v3.0.1_2019-nrt_Forest-Type-layer_EPSG-4326.tif?download=1'
dst=r'C:\grass_tmp\fty_2019.tif'
if not os.path.exists(dst) or os.path.getsize(dst) < 1_000_000_000:
    t=time.time()
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=120) as r, open(dst,'wb') as f:
        shutil.copyfileobj(r, f, 1024*1024)
    print('downloaded', os.path.getsize(dst), 'in', round(time.time()-t,1))
else:
    print('exists', os.path.getsize(dst))
