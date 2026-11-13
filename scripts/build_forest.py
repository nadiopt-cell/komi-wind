import numpy as np, rasterio, sys
from rasterio.windows import from_bounds
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds as fb, from_origin
from rasterio.crs import CRS
from PIL import Image
sys.path.insert(0,'scripts')
from common import *

src = r'C:\grass_tmp\fty_2019.tif'
with rasterio.open(src) as ds:
    win = from_bounds(44.0, 57.5, 67.5, 70.0, ds.transform)
    a = ds.read(1, window=win, boundless=True, fill_value=255)
    src_tr = ds.window_transform(win)
print('src', a.shape, np.unique(a, return_counts=True)[0])

# ---- AEA ----
dst = np.full((H, W), 255, dtype='uint8')
reproject(a, dst, src_transform=src_tr, src_crs='EPSG:4326',
          dst_transform=from_origin(X0, Y1, RES, RES), dst_crs=CRS.from_user_input(AEA),
          resampling=Resampling.nearest, src_nodata=255, dst_nodata=255)
np.save('build/forest_aea.npy', dst)
print('aea classes', np.unique(dst, return_counts=True))

# ---- web mercator ----
dem_m = np.load('build/dem_merc.npy')
Hm, Wm = dem_m.shape
from pyproj import Transformer
t = Transformer.from_crs(4326, 3857, always_xy=True)
x0,y0 = t.transform(45.30,58.90); x1,y1 = t.transform(66.40,68.60)
dst_m = np.full((Hm, Wm), 255, dtype='uint8')
reproject(a, dst_m, src_transform=src_tr, src_crs='EPSG:4326',
          dst_transform=fb(x0,y0,x1,y1,Wm,Hm), dst_crs='EPSG:3857',
          resampling=Resampling.nearest, src_nodata=255, dst_nodata=255)
np.save('build/forest_merc.npy', dst_m)

# ---- colorize ----
PAL = {1:(47,107,79), 3:(63,110,62), 4:(198,161,91), 5:(126,154,78)}
def colorize(arr, path, alpha=255):
    h,w = arr.shape
    out = np.zeros((h,w,4), dtype='uint8')
    for k,c in PAL.items():
        m = arr==k
        out[m,0]=c[0]; out[m,1]=c[1]; out[m,2]=c[2]; out[m,3]=alpha
    Image.fromarray(out, 'RGBA').save(path)
    return out
o1 = colorize(dst, 'build/forest_aea.png')
o2 = colorize(dst_m, 'web/data/forest_merc.png')
Image.fromarray(o1).resize((1000,1000), Image.NEAREST).save('build/preview_forest.png')
print('saved', o1.shape, o2.shape)
