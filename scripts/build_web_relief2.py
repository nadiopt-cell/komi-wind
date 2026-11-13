import numpy as np, rasterio, glob, sys
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from rasterio.vrt import WarpedVRT
from rasterio.crs import CRS
from pyproj import Transformer
from scipy import ndimage
from PIL import Image
sys.path.insert(0,'scripts')
from common import *

t = Transformer.from_crs(4326, 3857, always_xy=True)
x0, y0 = t.transform(45.30, 58.90)
x1, y1 = t.transform(66.40, 68.60)
Wm = 4200
Hm = int(round(Wm*(y1-y0)/(x1-x0)))
print('grid', Wm, Hm, 'res m/px', (x1-x0)/Wm)
tr = from_bounds(x0, y0, x1, y1, Wm, Hm)
crs = CRS.from_epsg(3857)
acc = np.zeros((Hm, Wm), 'float64'); cnt = np.zeros((Hm, Wm), 'uint8')
files = sorted(glob.glob(r'C:\grass_tmp\dem\*.tif'))
for i,f in enumerate(files):
    try:
        with rasterio.open(f) as src:
            with WarpedVRT(src, crs=crs, transform=tr, width=Wm, height=Hm,
                           resampling=Resampling.bilinear, src_nodata=src.nodata, nodata=-9999.0) as vrt:
                a = vrt.read(1, masked=True)
                m = (~a.mask) & (a.data > -1000) & (a.data < 9000)
                acc[m] += a.data[m]; cnt[m] += 1
    except Exception as e:
        print('ERR', f, e)
dem = np.where(cnt>0, acc/np.maximum(cnt,1), np.nan).astype('float32')
mask = np.isnan(dem)
if mask.any():
    ind = ndimage.distance_transform_edt(mask, return_distances=False, return_indices=True)
    dem = dem[tuple(ind)]
print('elev', dem.min(), dem.max())

# scale factor per row
lat = np.linspace(68.60, 58.90, Hm)
k = 1.0/np.cos(np.deg2rad(lat))[:,None]
res = (x1-x0)/Wm

def hs(az_deg, alt_deg=40.0, z=1.15):
    az=np.deg2rad(az_deg); alt=np.deg2rad(alt_deg)
    gy,gx = np.gradient(dem*z, res)
    gx = gx/k; gy = gy/k
    slope=np.arctan(np.hypot(gx,gy))
    aspect=np.arctan2(-gx,gy); aspect=np.where(aspect<0,2*np.pi+aspect,aspect)
    return np.clip(np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect),0,1)

shade = 0.46*hs(315)+0.22*hs(345)+0.17*hs(285)+0.15*hs(200)
p2,p98 = np.percentile(shade,[1,99])
shade = np.clip((shade-p2)/(p98-p2),0,1)**0.95

stops = [(0,(241,235,223)),(150,(234,226,211)),(300,(226,216,198)),(500,(215,202,184)),
         (800,(202,188,169)),(1100,(188,173,155)),(1500,(172,157,141)),(1900,(157,143,130))]
e = np.clip(dem,0,1900); rgb=np.zeros((Hm,Wm,3),'float32')
for i in range(len(stops)-1):
    e0,c0=stops[i]; e1,c1=stops[i+1]
    m=(e>=e0)&(e<e1); tt=(e[m]-e0)/(e1-e0)
    for c in range(3): rgb[m,c]=c0[c]+tt*(c1[c]-c0[c])
rgb[e>=stops[-1][0]] = stops[-1][1]
out = np.clip(rgb*(0.52+0.62*shade[...,None]),0,255).astype('uint8')
Image.fromarray(out).save('web/data/relief_merc.jpg', quality=87, optimize=True)
np.save('build/dem_merc.npy', dem); np.save('build/shade_merc.npy', shade.astype('float32'))
import json
json.dump({'bounds_merc':[x0,y0,x1,y1],'size':[Wm,Hm],'lonlat':[45.30,58.90,66.40,68.60]}, open('build/web_relief_meta.json','w'))
print('saved')
