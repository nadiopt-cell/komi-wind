import urllib.request, os, concurrent.futures, time
URL='https://zenodo.org/records/3939050/files/PROBAV_LC100_global_v3.0.1_2019-nrt_Forest-Type-layer_EPSG-4326.tif?download=1'
TOTAL=1037889222
parts_dir=r'C:\grass_tmp\fty_parts'
os.makedirs(parts_dir, exist_ok=True)
N=24
size=(TOTAL+N-1)//N
H={'User-Agent':'curl/8.4.0'}
def get(i):
    a=i*size; b=min(TOTAL-1,(i+1)*size-1)
    dst=os.path.join(parts_dir, f'part_{i:02d}')
    if os.path.exists(dst) and os.path.getsize(dst)==b-a+1: return i,True
    for att in range(5):
        try:
            req=urllib.request.Request(URL, headers={**H,'Range':f'bytes={a}-{b}'})
            with urllib.request.urlopen(req, timeout=120) as r, open(dst,'wb') as f:
                while True:
                    chunk=r.read(1<<20)
                    if not chunk: break
                    f.write(chunk)
            if os.path.getsize(dst)==b-a+1: return i,True
        except Exception as e:
            print('retry',i,e, flush=True)
            time.sleep(2)
    return i,False
t=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    res=list(ex.map(get, range(N)))
print('ok', sum(1 for _,o in res if o), 'in', round(time.time()-t,1), 's', flush=True)
if all(o for _,o in res):
    with open(r'C:\grass_tmp\fty_2019.tif','wb') as out:
        for i in range(N):
            with open(os.path.join(parts_dir,f'part_{i:02d}'),'rb') as f:
                while True:
                    c=f.read(8<<20)
                    if not c: break
                    out.write(c)
    print('assembled', os.path.getsize(r'C:\grass_tmp\fty_2019.tif'))
